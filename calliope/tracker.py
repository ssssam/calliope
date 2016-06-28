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
import sys

import calliope


def argument_parser():
    parser = argparse.ArgumentParser(
        description="Create playlists from your local music collection, using "
                    "the Tracker database")


class TrackerClient():
    def __init__(self):
        self.conn = Tracker.SparqlConnection.get(None)

    def artist(self, artist_name):
        '''Return the Tracker URN for a given artist.'''
        query_artist_urn = "SELECT ?u { ?u a nmm:MusicArtist ; nie:title \"%s\" }"
        result = self.conn.query(query_artist_urn % artist_name)
        return result[0]

    def songs_for_artist(self, artist_id):
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
                nmm:albumArtist %s .
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
                nmm:artist %s .
            OPTIONAL { ?track nmm:MusicAlbum ?album }
            FILTER (! bound (?album))
        } ORDER BY
            nie:title(?track)
        """

        self.conn.query(



def expand(tracker, item):
    if 'artist' not in item:
        # This restriction may become annoying, hopefully we can relax it.
        raise RuntimeError ('All items must specify at least "artist"')

    if 'song' in item:
        # Get just the song
        pass
    else:
        pass


def main():
    input_playlist_data = yaml.safe_load(sys.stdin)

    tracker = TrackerClient()

    for item in input_playlist_data:
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
