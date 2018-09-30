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


DEFAULT_APP_DOMAIN_DIR = os.path.join(xdg.BaseDirectory.xdg_data_home, 'calliope', 'tracker')


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

    def songs(self, filter_artist_name=None, filter_album_name=None, filter_track_name=None, track_search_text=None):
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
            assert track_search_text is None, "Cannot pass both filter_track_name and track_search_text"
            track_pattern = """
                ?track nie:title ?trackTitle .
                FILTER (LCASE(?trackTitle) = "%s")
            """  % Tracker.sparql_escape_string(filter_track_name.lower())
        elif track_search_text:
            track_pattern = """
                ?track nie:title ?trackTitle .
                FILTER (fn:contains(LCASE(?trackTitle), "%s"))
            """  % Tracker.sparql_escape_string(track_search_text.lower())
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

        result = []

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
        if len(album_tracks) > 0:
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
            if len(catchall_tracks) > 0:
                yield {
                    'artist': current_artist_name,
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
                list(tracker.songs(filter_artist_name=item.get('artist'), filter_track_name=str(track))))
    elif albums:
        for album in albums:
            result.extend(
                list(tracker.songs(filter_artist_name=item.get('artist'), filter_album_name=str(album))))
    else:
        result = list(tracker.songs(filter_artist_name=item['artist']))

    return result


def print_table(result_table):
    result_table.display()


@calliope.cli.group(name='tracker',
                    help="Query and manage the Tracker media database")
@click.option('--domain', type=str, default='app',
              help="Tracker domain to use. Specify 'app' for a private domain, "
                   "or 'session' for the session-wide Tracker instance. (Default: 'app')")
@click.option('--app-domain-dir', type=str, default=DEFAULT_APP_DOMAIN_DIR,
              help="when --domain=app, store data in DIR (default: {})".format(DEFAULT_APP_DOMAIN_DIR))
@click.pass_context
def tracker_cli(context, domain, app_domain_dir):
    if domain == 'app':
        # It seems messy calling the tracker_app_domain() context manager
        # directly here... but I'm not sure how else to get Click to run
        # the cleanup function.
        mgr = trackerappdomain.tracker_app_domain('uk.me.afuera.calliope', app_domain_dir)
        tracker_app_domain = mgr.__enter__()
        def cleanup():
            mgr.__exit__(None, None, None)
        context.call_on_close(cleanup)

        context.obj.app_domain = tracker_app_domain
        context.obj.sparql_connection = tracker_app_domain.connection()
    else:
        context.obj.app_domain = None
        if domain != 'session':
            Tracker.SparqlConnection.set_domain(domain)
        context.obj.sparql_connection = Tracker.SparqlConnection.get()

    context.obj.tracker_client = TrackerClient(context.obj.sparql_connection)


@tracker_cli.command(name='annotate')
@click.argument('playlist', type=click.File(mode='r'))
@click.pass_context
def cmd_annotate(context, playlist):
    '''Add information stored in a Tracker database to items in a playlist.'''
    tracker = context.obj.tracker_client

    for item in calliope.playlist.read(playlist_data):
        if 'location' in item:
            # This already has a URI!
            pass
        else:
            try:
                calliope.write([add_location(tracker, item)], sys.stdout)
            except RuntimeError as e:
                raise RuntimeError("%s\nItem: %s" % (e, item))


@tracker_cli.command(name='scan')
@click.argument('path', nargs=1, type=click.Path(exists=True))
@click.pass_context
def cmd_scan(context, path):
    '''Scan all media files under a particular path and update a Tracker database.

    This is only possible when `--domain=app`.'''
    app_domain = context.obj.app_domain

    if not app_domain:
        raise RuntimeError("Scanning specific directories is only possible when "
                           "using the app-specific Tracker domain.")

    loop = GLib.MainLoop.new(None, 0)

    def progress_callback(status, progress, remaining_time):
        sys.stderr.write("Status: {}, {}, {}\n".format(status, progress, remaining_time))

    def idle_callback():
        loop.quit()

    with trackerappdomain.glib_excepthook(loop):
        app_domain.index_location_async(path, progress_callback, idle_callback)
        loop.run()


@tracker_cli.command(name='search')
@click.argument('text', nargs=1, type=str)
@click.pass_context
def cmd_search(context, text):
    '''Search track titles in the Tracker database.'''
    tracker = context.obj.tracker_client
    calliope.playlist.write(tracker.songs(track_search_text=text), sys.stdout)


@tracker_cli.command(name='show')
@click.option('--artist', nargs=1, type=str,
              help="Limit results to the given artist")
@click.pass_context
def cmd_show(context, artist):
    '''Show all files that have metadata stored in a Tracker database.'''
    tracker = context.obj.tracker_client
    calliope.playlist.write(tracker.songs(filter_artist_name=artist), sys.stdout)


@tracker_cli.command(name='sparql')
@click.argument('query', nargs=1, type=str)
@click.pass_context
def cmd_sparql(context, query):
    '''Execute a SPARQL query.'''
    cursor = context.obj.sparql_connection.query(query)
    while cursor.next():
        values = [str(cursor.get_string(i)[0]) for i in range(0, cursor.get_n_columns())]
        print(", ".join(values))


@tracker_cli.command(name='top-artists')
@click.pass_context
@click.option('-c', '--count', type=int, default=20,
              help="Maximum number of artists to return")
def cmd_top_artists(context, count):
    '''Query the top artists in a Tracker database'''
    tracker = context.obj.tracker_client
    result = list(tracker.artists_by_number_of_songs(limit=count))
    calliope.playlist.write(result, sys.stdout)
