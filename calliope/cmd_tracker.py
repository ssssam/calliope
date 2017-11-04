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

import gi

try:
    gi.require_version('Tracker', '2.0')
except ValueError:
    gi.require_version('Tracker', '1.0')
from gi.repository import Tracker

import click
import yaml

import logging
import sys
import warnings

import calliope


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

        return calliope.OneShotResultsTable(
            headings=['Artist', 'Number of Songs'],
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
                ?album
                nie:title(?track)
                %s
            WHERE {
                ?track a nmm:MusicPiece .
                %s %s
                OPTIONAL { ?track nmm:musicAlbum ?album }
                FILTER (! bound (?album))
            } ORDER BY
                %s
                nie:title(?track)
            """ % (artist_select, artist_pattern, track_pattern, artist_select)

            songs_without_releases = self.query(
                query_songs_without_releases)
        else:
            songs_without_releases = None

        result = []

        # The artist name may be returned as None if it's unknown to Tracker,
        # so we can't use None as an 'undefined' value. int(-1) will work,
        # as any artist named "-1" would be returned as str("-1").
        prev_artist_name = -1
        prev_album_name = -1

        album_tracks = []
        while songs_with_releases.next():
            if artist_select:
                artist_name = songs_with_releases.get_string(3)[0]
            album_name = songs_with_releases.get_string(1)[0]

            if prev_artist_name is -1:
                prev_artist_name = artist_name
            if prev_album_name is -1:
                prev_album_name = album_name

            if album_name != prev_album_name:
                yield {
                    'artist': prev_artist_name,
                    'album': prev_album_name,
                    'tracks': album_tracks,
                }
                album_tracks = []
                prev_artist_name = artist_name
                prev_album_name = album_name

            album_tracks.append({
                'track': songs_with_releases.get_string(2)[0],
                'location': songs_with_releases.get_string(0)[0]
            })
        if len(album_tracks) > 0:
            yield {
                'artist': artist_name,
                'album': album_name,
                'tracks': album_tracks,
            }

        prev_artist_name = -1
        catchall_tracks = []
        if songs_without_releases:
            while songs_without_releases.next():
                if artist_select:
                    artist_name = songs_without_releases.get_string(3)[0]
                if prev_artist_name is -1:
                    prev_artist_name = artist_name
                if prev_artist_name != artist_name:
                    yield {
                        'artist': prev_artist_name,
                        'tracks': catchall_tracks
                    }
                    prev_artist_name = artist_name
                    catchall_tracks = []
                catchall_tracks.append({
                    'track': songs_without_releases.get_string(2)[0],
                    'location': songs_without_releases.get_string(0)[0]
                })
            if len(catchall_tracks) > 0:
                yield {
                    'artist': artist_name,
                    'tracks': catchall_tracks
                }


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
                list(tracker.songs(artist_name=item.get('artist'), track_name=str(track))))
    elif albums:
        for album in albums:
            result.extend(
                list(tracker.songs(artist_name=item.get('artist'), album_name=str(album))))
    else:
        result = list(tracker.songs(artist_name=item['artist']))

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


@calliope.cli.command(name='tracker')
@click.option('-d', '--debug', is_flag=True)
@click.option('--top', type=click.Choice(['artists']),
              help="show artists with the most tracks in the local collection")
@click.argument('playlist', nargs=-1, type=click.Path(exists=True))
def run(debug, top, playlist):
    '''Query music files on the local machine'''

    if debug:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    tracker = TrackerClient()

    if top != None:
        if top == 'artists':
            print_table(tracker.artists_by_number_of_songs(limit=None))
            return None
        else:
            raise RuntimeError("Unknown type: %s" % top)

    if len(playlist) == 0:
        print_collection(tracker.songs())
        return None
    else:
        input_playlists = (yaml.safe_load(open(p, 'r')) for p in playlist)

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
