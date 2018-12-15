# Calliope
# Copyright (C) 2016,2018  Sam Thursfield <sam@afuera.me.uk>
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

gi.require_version('Tracker', '2.0')
from gi.repository import GLib, Tracker

import click
import trackerappdomain

import logging
import os
import sys
import warnings
import xdg.BaseDirectory

import calliope

log = logging.getLogger(__name__)


class TrackerClient():
    '''Helper functions for querying from the user's Tracker database.'''

    def __init__(self, connection):
        self._conn = connection

    def query(self, query):
        '''Run a single SPARQL query.'''
        log.debug("Query: %s" % query)
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

        cursor = self.query(query)

        while cursor.next():
            artist_name = cursor.get_string(0)[0]
            n_songs = cursor.get_string(1)[0]
            yield {
                'artist': artist_name,
                'track-count': n_songs
            }

    def track(self, artist_name, track_name):
        '''Find a specific track by name.

        Tries to find a track matching the given artist and title.

        Returns a playlist entry, or None.

        '''
        query_track = """
        SELECT
            ?track_url
        WHERE {
            ?track a nmm:MusicPiece ;
              dc:title "%s" ;
              nie:url ?track_url ;
              nmm:performer ?artist .
            ?artist nmm:artistName "%s" .
        }""" % (track_name, artist_name)

        cursor = self.query(query_track)

        if cursor.next():
            return {
                'track': track_name,
                'artist': artist_name,
                'tracker.url': cursor.get_string(0)[0],
            }
        else:
            return {}

    def tracks(self, filter_artist_name=None, track_search_text=None):
        '''Return a list of tracks.'''

        if track_search_text:
            track_pattern = """
                FILTER (fn:contains(LCASE(?track_title), "%s"))
            """  % Tracker.sparql_escape_string(track_search_text.lower())
        else:
            track_pattern = " "

        if filter_artist_name:
            artist_pattern = 'FILTER (LCASE(?artist_name) = "%s")' % \
                Tracker.sparql_escape_string(filter_artist_name.lower())
        else:
            artist_pattern =" "

        query_tracks = """
        SELECT
            ?track_title ?track_url ?artist_name
        WHERE {
            ?track a nmm:MusicPiece ;
              dc:title ?track_title ;
              nie:url ?track_url ;
              nmm:performer ?artist .
            %s %s
            ?artist nmm:artistName ?artist_name .
        }
        ORDER BY ?track_title ?artist_name
        """ % (track_pattern, artist_pattern)

        tracks = self.query(query_tracks)
        while tracks.next():
            yield {
                'track': tracks.get_string(0)[0],
                'artist': tracks.get_string(2)[0],
                'tracker.url': tracks.get_string(1)[0],
            }

    def albums(self, filter_artist_name=None, filter_album_name=None, filter_track_name=None, ):
        '''Return all songs matching specific search criteria.

        These are grouped into their respective releases. Any tracks that
        aren't present on any releases will appear last. Any tracks that
        appear on multiple releases will appear multiple times.

        '''
        if filter_artist_name:
            artist_id = self.artist_id(filter_artist_name)
            artist_select = ""
            artist_pattern = """
                ?track nmm:performer <%s> .
            """ % artist_id
        else:
            artist_select = "nmm:artistName(?artist)"
            artist_pattern = "?track nmm:performer ?artist ."
        if filter_album_name:
            album_pattern = """
                ?album nie:title ?albumTitle .
                FILTER (LCASE(?albumTitle) = "%s")
            """  % Tracker.sparql_escape_string(filter_album_name.lower())
        else:
            album_pattern = ""
        if filter_track_name:
            track_pattern = """
                ?track nie:title ?trackTitle .
                FILTER (LCASE(?trackTitle) = "%s")
            """  % Tracker.sparql_escape_string(filter_track_name.lower())
        else:
            track_pattern = ""

        query_songs_with_releases = """
        SELECT
            nie:url(?track)
            nie:title(?album)
            nie:title(?track)
            %s
        WHERE {
            ?album a nmm:MusicAlbum .
            ?track a nmm:MusicPiece ;
                nmm:musicAlbum ?album .
            %s %s %s
        } ORDER BY
            nie:title(?album)
            nmm:trackNumber(?track)
        """ % (artist_select, artist_pattern, album_pattern, track_pattern)

        songs_with_releases = self.query(query_songs_with_releases)

        if not filter_album_name:
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

        # The artist name may be returned as None if it's unknown to Tracker,
        # so we can't use None as an 'undefined' value. int(-1) will work,
        # as any artist named "-1" would be returned as str("-1").
        prev_artist_name = -1
        prev_album_name = -1

        album_tracks = []
        while songs_with_releases.next():
            current_artist_name = filter_artist_name or songs_with_releases.get_string(3)[0]
            album_name = songs_with_releases.get_string(1)[0]

            if prev_artist_name is -1:
                prev_artist_name = current_artist_name
            if prev_album_name is -1:
                prev_album_name = album_name

            if album_name != prev_album_name:
                yield {
                    'artist': prev_artist_name,
                    'album': prev_album_name,
                    'tracks': album_tracks,
                }
                album_tracks = []
                prev_artist_name = current_artist_name
                prev_album_name = album_name

            album_tracks.append({
                'track': songs_with_releases.get_string(2)[0],
                'location': songs_with_releases.get_string(0)[0]
            })
        if album_tracks:
            yield {
                'artist': current_artist_name,
                'album': album_name,
                'tracks': album_tracks,
            }

        prev_artist_name = -1
        catchall_tracks = []
        if songs_without_releases:
            while songs_without_releases.next():
                current_artist_name = filter_artist_name or songs_without_releases.get_string(3)[0]
                if prev_artist_name is -1:
                    prev_artist_name = current_artist_name
                if prev_artist_name != current_artist_name:
                    yield {
                        'artist': prev_artist_name,
                        'tracks': catchall_tracks
                    }
                    prev_artist_name = current_artist_name
                    catchall_tracks = []
                catchall_tracks.append({
                    'track': songs_without_releases.get_string(2)[0],
                    'location': songs_without_releases.get_string(0)[0]
                })
            if catchall_tracks:
                yield {
                    'artist': current_artist_name,
                    'tracks': catchall_tracks
                }

    def artists(self):
        '''Return all artists who have at least one track available locally.'''
        query_artists_with_tracks = """
        SELECT
            ?artist_name
        {   ?artist a nmm:Artist ;
            dc:title ?artist_name .
            ?song nmm:performer ?artist
        }
        GROUP BY ?artist ORDER BY ?artist_name
        """

        artists_with_tracks = self.query(query_artists_with_tracks)

        while artists_with_tracks.next():
            artist_name = artists_with_tracks.get_string(0)[0]
            yield {
                'artist': artist_name,
            }


class TrackerContext():
    def __init__(self, domain, app_domain_dir):
        if domain == 'app':
            # It seems messy calling the tracker_app_domain() context manager
            # directly here... but I'm not sure how else to get Click to run
            # the cleanup function.
            self._mgr = trackerappdomain.tracker_app_domain('uk.me.afuera.calliope', app_domain_dir)
            tracker_app_domain = self._mgr.__enter__()  # pylint: disable=no-member

            self.app_domain = tracker_app_domain
            self.sparql_connection = tracker_app_domain.connection()
        else:
            self._mgr = None
            self.app_domain = None
            if domain != 'session':
                Tracker.SparqlConnection.set_domain(domain)
            self.sparql_connection = Tracker.SparqlConnection.get()

        self.client = TrackerClient(self.sparql_connection)

    def cleanup(self):
        if self._mgr is not None:
            self._mgr.__exit__(None, None, None)    # pylint: disable=no-member


def add_location(tracker, item):
    if 'track' not in item:
        # We can only add location for 'track' items.
        return item

    tracker_item = tracker.track(artist_name=item['artist'], track_name=item['track'])

    if tracker_item:
        item.update(tracker_item)
    else:
        warnings = item.get('warnings', [])
        warnings.append('tracker: Unknown track')
        item['warnings'] = warnings

    return item


def annotate(tracker, playlist):
    playlist=list(playlist)
    for item in playlist:
        try:
            item = add_location(tracker.client, item)
        except RuntimeError as e:
            raise RuntimeError("%s\nItem: %s" % (e, item))

        yield item


def execute_sparql(tracker, query):
    cursor = tracker.sparql_connection.query(query)
    while cursor.next():
        values = [str(cursor.get_string(i)[0]) for i in range(0, cursor.get_n_columns())]
        print(", ".join(values))


def expand_tracks(tracker, playlist):
    for item in playlist:
        if 'track' in item or 'tracks' in item:
            yield item
        else:
            tracks = tracker.tracks(filter_artist_name=item['artist'])
            yield from tracks


def scan(tracker, path):
    app_domain = tracker.app_domain

    if not app_domain:
        raise RuntimeError("Scanning specific directories is only possible when "
                           "using the app-specific Tracker domain.")

    loop = trackerappdomain.MainLoop()

    def progress_callback(status, progress, remaining_time):
        sys.stderr.write("Status: {}, {}, {}\n".format(status, progress, remaining_time))

    def idle_callback():
        loop.quit()

    app_domain.index_location_async(path, progress_callback, idle_callback)
    loop.run_checked()
