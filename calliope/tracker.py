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

'''calliope-tracker'''

import gi
gi.require_version('Tracker', '1.0')

from gi.repository import Tracker

import yaml

import argparse
import itertools
import logging
import sys

import calliope


def argument_parser():
    parser = argparse.ArgumentParser(
        description="Create playlists from your local music collection, using "
                    "the Tracker database")
    parser.add_argument('playlist', nargs='*',
                        help="playlist file")
    parser.add_argument('-d', '--debug', action='store_true',
                        help="enable verbose debug output")

    parser.add_argument('--top', choices=['artists'],
                        help="show the top artists (by number of songs)")

    return parser


class TrackerClient():
    def __init__(self):
        self._conn = Tracker.SparqlConnection.get(None)

    def query(self, query):
        logging.debug("Query: %s" % query)
        return self._conn.query(query)

    def artist_id(self, artist_name):
        '''Return the Tracker URN for a given artist.'''
        query_artist_urn = "SELECT ?u { ?u a nmm:Artist ; dc:title \"%s\" }"
        result = self.query(query_artist_urn % artist_name)

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

    def artists_by_number_of_songs(self, limit=1):
        '''Return a list of artists by number of songs known.'''
        query_artists_by_number_of_songs = """
        SELECT ?artist_name (COUNT(?song) as ?songs)
          { ?artist a nmm:Artist ;
                dc:title ?artist_name .
            ?song nmm:performer ?artist }
        GROUP BY ?artist ORDER BY DESC(?songs)
        LIMIT %i
        """
        result = self.query(query_artists_by_number_of_songs % limit)

        while result.next():
            artist_name = result.get_string(0)[0]
            n_songs = result.get_string(1)[0]

            print("%s: %s" % (artist_name, n_songs))


    def songs_for_artist(self, artist_id, artist_name=None):
        '''Return all songs for a given artist.

        These are grouped into their respective releases. Any tracks that
        aren't present on any releases will appear last. Any tracks that
        appear on multiple releases will appear multiple times.

        '''

        query_songs_with_releases = """
        SELECT
            nie:url(?track)
            nmm:albumTitle(?album)
            nie:title(?track)
        WHERE {
            ?album a nmm:MusicAlbum ;
                nmm:albumArtist <%s> .
            ?track a nmm:MusicPiece ;
                nmm:musicAlbum ?album
        } ORDER BY
            nmm:albumTitle(?album)
            nmm:trackNumber(?track)
        """

        query_songs_without_releases = """
        SELECT
            nie:url(?track)
            nie:title(?track)
        WHERE {
            ?track a nmm:MusicPiece ;
                nmm:performer <%s> .
            OPTIONAL { ?track nmm:musicAlbum ?album }
            FILTER (! bound (?album))
        } ORDER BY
            nie:title(?track)
        """

        songs_with_releases = self.query(query_songs_with_releases % artist_id)
        songs_without_releases = self.query(query_songs_without_releases % artist_id)

        if not artist_name:
            artist_name = self.artist_name(artist_id)

        result = []
        prev_album_name = None
        album_tracks = None
        while songs_with_releases.next():
            album_name = songs_with_releases.get_string(1)[0]
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
        while songs_without_releases.next():
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

        return yaml.dump(result)


def expand(tracker, item):
    if 'artist' not in item:
        # This restriction may become annoying, hopefully we can relax it.
        raise RuntimeError ('All items must specify at least "artist": got %s'
                            % item)

    artist = tracker.artist_id(item['artist'])
    if artist is None:
        return "# Did not find any music for artist: %s\n" % item['artist']

    if 'song' in item:
        # Get just the song
        pass
    else:
        return tracker.songs_for_artist(artist)


def main():
    args = argument_parser().parse_args()
    if args.debug:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    tracker = TrackerClient()

    if args.top != None:
        if args.top == 'artists':
            tracker.artists_by_number_of_songs(limit=100)
            return None
        else:
            raise RuntimeError("Unknown type: %s" % args.top)

    if args.playlist == None:
        input_playlists = yaml.safe_load_all(sys.stdin)
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
                print(expand(tracker, item))


try:
    main()
except RuntimeError as e:
    sys.stderr.write("ERROR: %s\n" % e)
    sys.exit(1)
