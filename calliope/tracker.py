#!/usr/bin/env python3
# Calliope
# Copyright (C) 2016  Sam Thursfield <sam@afuera.me.uk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

'''calliope-tracker

Provides a commandline interface for querying the music files stored on this
computer, using the 'Tracker' indexing tool.
'''

import gi
gi.require_version('Tracker', '1.0')

from gi.repository import Tracker

import yaml

import argparse
import logging
import sys
import warnings

import calliope


class OneShotResultsTable():
    '''A class for wrapping a generator that contains data.

    This is a way of returning a database cursor, without dumping it straight
    to stdout, and without reading the whole thing in to memory. The catch is
    that only one method which reads the cursor can ever be called, because we
    can't rewind the cursor afterwards.

    '''

    def __init__(self, headings, generator):
        '''Create a results table holder.

        The generator should return a single row for each call to next(). Each
        row should be a list of N elements, and there must also be N headings.

        '''
        self.headings = headings
        self.generator = generator
        self.dead = False

    def headings(self):
        return self.headings

    def display(self):
        '''Print the held data to stdout. Can only be called once.'''
        if self.dead:
            raise RuntimeError("Results table has already been used.")
        for row in self.generator:
            if len(row) != len(self.headings):
                warnings.warn("Number of columns doesn't match number of "
                              "headings!")
            print("\t".join(row))
        self.dead = True


def argument_parser():
    parser = argparse.ArgumentParser(
        description="Create playlists from your local music collection, using "
                    "the Tracker database")
    parser.add_argument('playlist', nargs='*',
                        help="playlist file")
    parser.add_argument('-d', '--debug', action='store_true',
                        help="enable verbose debug output")

    parser.add_argument('--top', choices=['artists'],
                        help="show the top artists by number of songs in the "
                             "Tracker collection")

    # The default behaviour, if no input playlists are given and no actions are
    # given, is to print the entire collection to stdout.

    return parser


class TrackerClient():
    '''Helper functions for querying from the user's Tracker database.'''

    def __init__(self):
        self._conn = Tracker.SparqlConnection.get(None)

    def query(self, query):
        '''Run a single SPARQL query.'''
        logging.debug("Query: %s" % query)
        return self._conn.query(query)

    def artist_id(self, artist_name):
        '''Return the Tracker URN for a given artist.'''
        query_artist_urn = """
        SELECT ?u {
            ?u a nmm:Artist ;
                dc:title ?name .
            FILTER (LCASE(?name) = "%s")
        }"""
        result = self.query(query_artist_urn % artist_name.lower())

        if result.next():
            return result.get_string(0)[0]
        else:
            return None

    def artist_name(self, artist_id):
        '''Return the name of a given artist.'''
        query_artist_name = "SELECT ?name { <%s> a nmm:Artist ; dc:title ?name }"
        result = self.query(query_artist_name % artist_id)

        if result.next():
            return result.get_string(0)[0]
        else:
            return None

    def artists_by_number_of_songs(self, limit=None):
        '''Return a list of artists by number of songs known.'''
        query_artists_by_number_of_songs = """
        SELECT ?artist_name (COUNT(?song) as ?songs)
          { ?artist a nmm:Artist ;
                dc:title ?artist_name .
            ?song nmm:performer ?artist }
        GROUP BY ?artist ORDER BY DESC(?songs) ?artist_name
        """

        if limit is not None:
            query = query_artists_by_number_of_songs + " LIMIT %i" % limit
        else:
            query = query_artists_by_number_of_songs

        result_cursor = self.query(query)

        def result_generator_fn(cursor):
            while cursor.next():
                artist_name = cursor.get_string(0)[0]
                n_songs = cursor.get_string(1)[0]
                yield artist_name, n_songs

        return OneShotResultsTable(headings=['Artist', 'Number of Songs'],
                                   generator=result_generator_fn(result_cursor))


    def songs(self, artist_name=None, album_name=None, track_name=None):
        '''Return all songs matching specific search criteria.

        These are grouped into their respective releases. Any tracks that
        aren't present on any releases will appear last. Any tracks that
        appear on multiple releases will appear multiple times.

        '''
        if artist_name:
            artist_id = self.artist_id(artist_name)
            artist_select = ""
            artist_pattern = """
                ?track nmm:performer <%s> .
            """ % artist_id
        else:
            artist_select = "nmm:artistName(nmm:performer(?track))"
            artist_pattern = ""
        if album_name:
            album_pattern = """
                ?album nie:title ?albumTitle .
                FILTER (LCASE(?albumTitle) = "%s")
            """  % Tracker.sparql_escape_string(album_name.lower())
        else:
            album_pattern = ""
        if track_name:
            track_pattern = """
                ?track nie:title ?trackTitle .
                FILTER (LCASE(?trackTitle) = "%s")
            """  % Tracker.sparql_escape_string(track_name.lower())
        else:
            track_pattern = ""

        query_songs_with_releases = """
        SELECT
            nie:url(?track)
            nmm:albumTitle(?album)
            nie:title(?track)
            %s
        WHERE {
            ?album a nmm:MusicAlbum .
            ?track a nmm:MusicPiece ;
                nmm:musicAlbum ?album .
            %s %s %s
        } ORDER BY
            nmm:albumTitle(?album)
            nmm:trackNumber(?track)
        """ % (artist_select, artist_pattern, album_pattern, track_pattern)

        songs_with_releases = self.query(query_songs_with_releases)

        if not album_name:
            query_songs_without_releases = """
            SELECT
                nie:url(?track)
                nie:title(?track)
                %s
            WHERE {
                ?track a nmm:MusicPiece .
                %s %s
                OPTIONAL { ?track nmm:musicAlbum ?album }
                FILTER (! bound (?album))
            } ORDER BY
                nie:title(?track)
            """ % (artist_select, artist_pattern, track_pattern)

            songs_without_releases = self.query(
                query_songs_without_releases)
        else:
            songs_without_releases = None

        result = []
        prev_album_name = None
        album_tracks = None
        while songs_with_releases.next():
            album_name = songs_with_releases.get_string(1)[0]
            if artist_select:
                artist_name = songs_with_releases.get_string(3)[0]
            if album_name != prev_album_name:
                album_tracks = []
                result.append(
                    {'artist': artist_name,
                     'album': album_name,
                     'tracks': album_tracks,
                })
                prev_album_name = album_name

            album_tracks.append({
                'track': songs_with_releases.get_string(2)[0],
                'location': songs_with_releases.get_string(0)[0]
            })

        catchall_tracks = None
        if songs_without_releases:
            while songs_without_releases.next():
                if artist_select:
                    artist_name = songs_with_releases.get_string(3)[0]
                if not catchall_tracks:
                    catchall_tracks = []
                    result.append(
                        {'artist': artist_name,
                        'tracks': catchall_tracks
                    })
                catchall_tracks.append({
                    'track': songs_with_releases.get_string(2)[0],
                    'location': songs_with_releases.get_string(0)[0]
                })

        if len(result) > 0:
            return result
        else:
            return []


def add_location(tracker, item):
    if 'artist' not in item and 'album' not in item and 'track' not in item:
        raise RuntimeError (
            "All items must specify at least 'artist', 'album' or 'track': got %s" %
            item)

    albums = []
    tracks = []
    if 'albums' in item:
        if 'album' in item:
            raise RuntimeError("Only one of 'album' and 'albums' may be "
                               "specified.")
        if 'tracks' in item or 'track' in item:
            raise RuntimeError("You cannot use 'track' or 'tracks' with "
                               "'albums'")
        albums = item['albums']
    elif 'album' in item:
        if 'tracks' in item or 'track' in item:
            raise RuntimeError("You cannot use 'track' or 'tracks' with "
                               "'album'")
        albums = [item['album']]

    if 'tracks' in item:
        if 'track' in item:
            raise RuntimeError("Only one of 'track' and 'tracks' may be "
                               "specified.")
        tracks = item['tracks']
    elif 'track' in item:
        tracks = [item['track']]

    result = []

    if tracks:
        for track in tracks:
            result.extend(
                tracker.songs(artist_name=item.get('artist'), track_name=str(track)))
    elif albums:
        for album in albums:
            result.extend(
                tracker.songs(artist_name=item.get('artist'), album_name=str(album)))
    else:
        result = tracker.songs(artist_name=item['artist'])

    if len(result) > 0:
        return yaml.dump(result)
    else:
        warnings.warn("No results found for %s" % item)
        return "# No results found for %s" % item


def print_table(result_table):
    result_table.display()


def print_collection(result):
    print('collection:')
    for item in result:
        print(yaml.dump(item))


def main():
    args = argument_parser().parse_args()
    if args.debug:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    tracker = TrackerClient()

    if args.top != None:
        if args.top == 'artists':
            print_table(tracker.artists_by_number_of_songs(limit=None))
            return None
        else:
            raise RuntimeError("Unknown type: %s" % args.top)

    if len(args.playlist) == 0:
        print_collection(tracker.songs())
        return None
    else:
        input_playlists = (yaml.safe_load(open(playlist, 'r')) for playlist in args.playlist)

    # FIXME: should be a collection if any inputs are collections, otherwise a
    # playlist
    print('collection:')
    for playlist_data in input_playlists:
        for item in calliope.Playlist(playlist_data):
            if 'location' in item:
                # This already has a URI!
                pass
            else:
                try:
                    print(add_location(tracker, item))
                except RuntimeError as e:
                    raise RuntimeError("%s\nItem: %s" % (e, item))


def pretty_warnings(message, category, filename, lineno,
                    file=None, line=None):
    return 'WARNING: %s\n' % (message)

warnings.formatwarning = pretty_warnings

try:
    main()
except BrokenPipeError:
    # This happens when we're piped to `less` or something, it's harmless
    pass
except RuntimeError as e:
    sys.stderr.write("ERROR: %s\n" % e)
    sys.exit(1)
