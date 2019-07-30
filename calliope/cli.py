# Calliope
# Copyright (C) 2018  Sam Thursfield <sam@afuera.me.uk>
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

'''Calliope command line interface.

This module provides the public command line interface for Calliope.

'''

import click
import parsedatetime
import xdg.BaseDirectory

import logging
import os
import sys

import calliope


# The CLI is defined using the Click module. Every command is declared
# in this module.
#
# CLI documentation is auto-generated from this module using 'sphinx-click'.
# There is a special flag that can be set to stub out the actual code, which
# exists so that this module can be imported by `sphinx-build` without pulling
# in the rest of Calliope and the many external dependencies that it requires.
# This makes it simple to build and host our documentation on readthedocs.org.


class App:
    def __init__(self, debug=False):
        self.debug = debug


@click.group()
@click.option('-d', '--debug', is_flag=True)
@click.pass_context
def cli(context, **kwargs):
    '''Calliope is a set of tools for processing playlists.'''

    context.obj = App(**kwargs)

    if context.obj.debug:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)


@cli.command(name='diff', help="Compare multiple collections")
@click.argument('playlist1', type=click.File(mode='r'))
@click.argument('playlist2', type=click.File(mode='r'))
@click.pass_context
def cmd_diff(context, playlist1, playlist2):
    result = calliope.diff.diff(calliope.playlist.read(playlist1),
                                calliope.playlist.read(playlist2))
    calliope.playlist.write(result, sys.stdout)


@cli.command(name='export')
@click.option('-f', '--format', type=click.Choice(['cue', 'm3u', 'jspf', 'xspf']), default='xspf')
@click.argument('playlist', nargs=1, type=click.File('r'))
@click.pass_context
def cmd_export(context, format, playlist):
    '''Convert to a different playlist format'''

    if format == 'cue':
        print(calliope.export.convert_to_cue(calliope.playlist.read(playlist)))
    elif format == 'm3u':
        print(calliope.export.convert_to_m3u(calliope.playlist.read(playlist)))
    elif format == 'jspf':
        print(calliope.export.convert_to_jspf(calliope.playlist.read(playlist)))
    elif format == 'xspf':
        print(calliope.export.convert_to_xspf(calliope.playlist.read(playlist)))
    else:
        raise NotImplementedError("Unsupport format: %s" % format)


@cli.command(name='import')
@click.argument('playlist', nargs=1, type=click.File('r'))
@click.pass_context
def cmd_import(context, playlist):
    '''Import playlists from other formats'''

    text = playlist.read()
    playlist = calliope.import_.import_(text)
    calliope.playlist.write(playlist, sys.stdout)


@cli.group(name='lastfm', help="Interface to the Last.fm music database")
@click.option('--user', metavar='NAME',
              help="show data for the given Last.fm user")
@click.pass_context
def lastfm_cli(context, user):
    context.obj.lastfm = calliope.lastfm.LastfmContext(user=user)


@lastfm_cli.command(name='annotate-tags')
@click.argument('playlist', type=click.File(mode='r'))
@click.pass_context
def lastfm_annotate_tags(context, playlist):
    '''Annotate playlist with tags from Last.fm'''

    context.obj.lastfm.authenticate()
    result_generator = calliope.lastfm.annotate_tags(
        context.obj.lastfm, calliope.playlist.read(playlist))
    calliope.playlist.write(result_generator, sys.stdout)


@lastfm_cli.command(name='similar-artists')
@click.pass_context
@click.option('-c', '--count', type=int, default=20,
              help="Maximum number of artists to return")
@click.argument('ARTIST')
def cmd_lastfm_similar_artists(context, count, artist):
    '''Return similar artists for a given artist name.'''

    output = calliope.lastfm.similar_artists(context.obj.lastfm, count,
                                             artist)
    calliope.playlist.write(output, sys.stdout)


@lastfm_cli.command(name='similar-tracks')
@click.pass_context
@click.option('-c', '--count', type=int, default=20,
              help="Maximum number of tracks to return")
@click.argument('ARTIST')
@click.argument('TRACK')
def cmd_lastfm_similar_artists(context, count, artist, track):
    '''Return similar tracks for a given track.'''

    output = calliope.lastfm.similar_tracks(context.obj.lastfm, count,
                                            artist, track)
    calliope.playlist.write(output, sys.stdout)


@lastfm_cli.command(name='top-artists')
@click.pass_context
@click.option('-c', '--count', type=int, default=20,
              help="Maximum number of artists to return")
@click.option('--time-range', default='overall',
              type=click.Choice(['overall', '7day', '1month', '3month',
                                 '6month', '12month']))
@click.option('--include', '-i', type=click.Choice(['images']), multiple=True)
def cmd_lastfm_top_artists(context, count, time_range, include):
    '''Return user's top artists.'''

    context.obj.lastfm.authenticate()
    result = calliope.lastfm.top_artists(context.obj.lastfm, count, time_range,
                                         include)
    calliope.playlist.write(output, sys.stdout)


@cli.group(name='lastfm-history',
           help="Scrape and query user's LastFM listening history")
@click.option('--sync/--no-sync', default=True,
              help="update the local copy of the LastFM history")
@click.option('--user', metavar='NAME',
              help="show data for the given Last.fm user")
@click.pass_context
def lastfm_history_cli(context, sync, user):
    context.obj.lastfm = calliope.lastfm.LastfmContext(user=user)

    lastfm_history = calliope.lastfm.history.load(context.obj.lastfm.user)
    if sync:
        lastfm_history.sync()

    context.obj.lastfm_history = lastfm_history


@lastfm_history_cli.command(name='scrobbles',
                            help="Export individual scrobbles as a playlist")
@click.pass_context
def cmd_lastfm_history_scrobbles(context):
    lastfm_history = context.obj.lastfm_history
    tracks = lastfm_history.scrobbles()
    calliope.playlist.write(tracks, sys.stdout)


@lastfm_history_cli.command(name='artists',
                            help="Query artists from the listening history")
@click.option('--first-play-before', metavar='DATE',
              help="show artists that were first played before DATE")
@click.option('--first-play-since', metavar='DATE',
              help="show artists that were first played on or after DATE")
@click.option('--last-play-before', metavar='DATE',
              help="show artists that were last played before DATE")
@click.option('--last-play-since', metavar='DATE',
              help="show artists that were last played on or after DATE")
@click.option('--min-listens', default=1, metavar='N',
              help="show only artists that were played N times")
@click.pass_context
def cmd_lastfm_history_artists(context, first_play_before, first_play_since,
                               last_play_before, last_play_since, min_listens):
    lastfm_history = context.obj.lastfm_history

    cal = parsedatetime.Calendar()

    if first_play_before is not None:
        first_play_before = cal.parse(first_play_before)
    if first_play_since is not None:
        first_play_since = cal.parse(first_play_since)
    if last_play_before is not None:
        last_play_before = cal.parse(last_play_before)
    if last_play_since is not None:
        last_play_since = cal.parse(last_play_since)

    artists = lastfm_history.artists(
        first_play_before=first_play_before,
        first_play_since=first_play_since,
        last_play_before=last_play_before,
        last_play_since=last_play_since,
        min_listens=min_listens)
    calliope.playlist.write(artists, sys.stdout)

@lastfm_history_cli.command(name='tracks',
                            help="Query tracks from the listening history")
@click.option('--first-play-before', metavar='DATE',
              help="show tracks that were first played before DATE")
@click.option('--first-play-since', metavar='DATE',
              help="show tracks that were first played on or after DATE")
@click.option('--last-play-before', metavar='DATE',
              help="show tracks that were last played before DATE")
@click.option('--last-play-since', metavar='DATE',
              help="show tracks that were last played on or after DATE")
@click.option('--min-listens', default=1, metavar='N',
              help="show only tracks that were played N times")
@click.pass_context
def cmd_lastfm_history_tracks(context, first_play_before, first_play_since,
                              last_play_before, last_play_since, min_listens):
    lastfm_history = context.obj.lastfm_history

    cal = parsedatetime.Calendar()

    if first_play_before is not None:
        first_play_before = cal.parse(first_play_before)
    if first_play_since is not None:
        first_play_since = cal.parse(first_play_since)
    if last_play_before is not None:
        last_play_before = cal.parse(last_play_before)
    if last_play_since is not None:
        last_play_since = cal.parse(last_play_since)

    tracks = lastfm_history.tracks(
        first_play_before=first_play_before,
        first_play_since=first_play_since,
        last_play_before=last_play_before,
        last_play_since=last_play_since,
        min_listens=min_listens)
    calliope.playlist.write(tracks, sys.stdout)


@cli.command(name='musicbrainz')
@click.argument('playlist', type=click.File(mode='r'))
@click.option('--include', '-i', type=click.Choice(['urls']), multiple=True)
@click.pass_context
def cmd_musicbrainz(context, playlist, include):
    '''Annotate playlists with data from Musicbrainz'''

    result_generator = calliope.musicbrainz.annotate(
        calliope.playlist.read(playlist), include)
    calliope.playlist.write(result_generator, sys.stdout)


@cli.command(name='play')
@click.option('-o', '--output', type=click.Path(), required=True)
@click.argument('playlist', type=click.File(mode='r'))
@click.pass_context
def cmd_play(context, output, playlist):
    '''Render a Calliope playlist to an audio file'''

    output_playlist = calliope.play.play(calliope.playlist.read(playlist),
                                         output)
    if output_playlist is not None:
        calliope.playlist.write(output_playlist, sys.stdout)


@cli.command(name='shuffle')
@click.option('--count', '-c', type=int, default=None,
              help="number of songs to output")
@click.argument('playlist', type=click.File(mode='r'))
@click.pass_context
def cmd_shuffle(context, count, playlist):
    '''Shuffle a playlist or collection.'''

    output = calliope.shuffle.shuffle(calliope.playlist.read(playlist), count)
    calliope.playlist.write(output, sys.stdout)


@cli.group(name='spotify',
                    help="Interface to the Spotify online streaming service")
@click.option('--token',
              help="use the given API access token")
@click.option('--user',
              help="show data for the given Spotify user")
@click.pass_context
def spotify_cli(context, token, user):
    if os.environ.get('CALLIOPE_SPOTIFY_MOCK') == 'yes':
        # This is for testing; as we currently run Calliope as a subprocess
        # from the test suite (due to trackerappdomain bugs when run multiple
        # times in the same process) we can't use mock.patch().
        import unittest.mock
        context.obj.spotify = unittest.mock.MagicMock()
    else:
        context.obj.spotify = calliope.spotify.SpotifyContext(user=user)
        context.obj.spotify.authenticate(token)


@spotify_cli.command(name='annotate')
@click.argument('playlist', type=click.File(mode='r'))
@click.pass_context
def cmd_spotify_annotate(context, playlist):
    '''Add Spotify-specific information to tracks in a playlist.'''
    api = context.obj.spotify.api

    for track in calliope.playlist.read(playlist):
        track = calliope.spotify.annotate_track(api, track)
        calliope.playlist.write([track], sys.stdout)


@spotify_cli.command(name='export')
@click.pass_context
def cmd_spotify_export(context):
    '''Query user playlists from Spotify'''
    calliope.spotify.export(context.obj.spotify)


@spotify_cli.command(name='import')
@click.pass_context
def cmd_spotify_import(context):
    '''Upload one or more playlists to Spotify'''
    raise NotImplementedError


@spotify_cli.command(name='top-artists')
@click.pass_context
@click.option('-c', '--count', type=int, default=20,
              help="Maximum number of artists to return")
@click.option('--time-range', default='long_term',
              type=click.Choice(['short_term', 'medium_term', 'long_term']))
def cmd_spotify_top_artists(context, count, time_range):
    '''Return user's top artists.'''
    result = calliope.spotify.top_artists(context.obj.spotify, count, time_range)

    calliope.playlist.write(result, sys.stdout)


@cli.command(name='stat')
@click.option('--size', '-s', is_flag=True,
              help="show the total size on disk of the playlist contents")
@click.argument('playlist', type=click.File(mode='r'))
@click.pass_context
def cmd_stat(context, size, playlist):
    '''Information about the contents of a playlist'''

    input_playlist = list(calliope.playlist.read(playlist))

    if size:
        calliope.stat.measure_size(input_playlist)
    else:
        print("Please select a mode.")


@cli.group(name='suggest', help="Suggest items or annotations")
@click.pass_context
def suggest_cli(context):
    pass


@suggest_cli.command(name='tracks')
@click.option('--from', 'from_', required=True, type=click.File(mode='r'),
              help="playlist from which tracks should be suggested")
@click.option('--count', type=int, default=10,
              help="number of track suggestions to generate")
@click.option('--training-input', multiple=True,
              type=(click.File(mode='r'), float),
              help="a playlist used to train the recommender. "
                   "A training input requires two arguments, the first is the "
                   "path to the file, the second is how it should weight the "
                   "training. Weight should be a value between -1.0 and 1.0, "
                   "where 1.0 is the most positive weighting and -1.0 the "
                   "most negative.")
@click.pass_context
def cmd_suggest_tracks(context, from_, count, training_input):
    '''Suggest tracks from a collection based on the given training inputs.'''

    # First we need a 'user-item' interaction matrix. Each 'item' is a track in
    # the input collection. Each 'user' is one of the input playlists.

    corpus_playlist = calliope.playlist.read(from_)
    calliope.suggest.suggest_tracks(corpus_playlist, count, training_input)


@cli.command(name='sync')
@click.option('--dry-run', is_flag=True,
              help="don't execute commands, only print what would be done")
@click.option('--target', '-t', type=click.Path(exists=True, file_okay=False),
              help="path to target device's filesystem")
@click.option('--allow-formats', '-f', type=click.Choice(['all', 'mp3']),
              multiple=True, default=[],
              help="specify formats that the target device can read; "
                   "transcoding can be done if needed.")
@click.option('--album-per-dir', is_flag=True,
              help="organise the files on the target device so each album is "
                   "in its own directory")
@click.option('--number-dirs', is_flag=True,
              help="ensure directory sort order matches desired playback "
                   "order")
@click.option('--number-files', is_flag=True,
              help="ensure filename sort order matches desired playback order")
@click.argument('playlist', type=click.File(mode='r'))
@click.pass_context
def cmd_sync(context, dry_run, target, allow_formats, album_per_dir,
             number_dirs, number_files, playlist):
    '''Copy playlists & collections between devices'''
    calliope.sync.sync(dry_run, target, allow_formats, album_per_dir,
                       number_files, number_files,
                       calliope.playlist.read(playlist))


TRACKER_DEFAULT_APP_DOMAIN_DIR = os.path.join(xdg.BaseDirectory.xdg_data_home, 'calliope', 'tracker')


@cli.group(name='tracker', help="Query and manage the Tracker media database")
@click.option('--domain', type=str, default='app',
              help="Tracker domain to use. Specify 'app' for a private domain, "
                   "or 'session' for the session-wide Tracker instance. (Default: 'app')")
@click.option('--app-domain-dir', type=str, default=TRACKER_DEFAULT_APP_DOMAIN_DIR,
              help="when --domain=app, store data in DIR (default: {})".format(TRACKER_DEFAULT_APP_DOMAIN_DIR))
@click.pass_context
def tracker_cli(context, domain, app_domain_dir):
    context.obj.tracker = calliope.tracker.TrackerContext(domain,
                                                          app_domain_dir)
    context.call_on_close(context.obj.tracker.cleanup)


@tracker_cli.command(name='annotate')
@click.argument('playlist', type=click.File(mode='r'))
@click.pass_context
def cmd_tracker_annotate(context, playlist):
    '''Add information stored in a Tracker database to items in a playlist.'''
    output = calliope.tracker.annotate(context.obj.tracker, calliope.playlist.read(playlist))
    calliope.playlist.write(output, sys.stdout)


@tracker_cli.command(name='expand-tracks')
@click.argument('playlist', type=click.File(mode='r'))
@click.pass_context
def cmd_tracker_expand_tracks(context, playlist):
    '''Convert any 'artist' or 'album' type playlist items into 'track' items'''
    result = calliope.tracker.expand_tracks(context.obj.tracker.client, calliope.playlist.read(playlist))
    calliope.playlist.write(result, sys.stdout)


@tracker_cli.command(name='local-albums')
@click.option('--artist', nargs=1, type=str,
              help="Limit to albums by the given artist")
@click.pass_context
def cmd_tracker_local_albums(context, artist):
    '''Show all albums available locally..'''
    tracker = context.obj.tracker.client
    calliope.playlist.write(tracker.albums(filter_artist_name=artist), sys.stdout)


@tracker_cli.command(name='local-artists')
@click.pass_context
def cmd_tracker_local_artists(context):
    '''Show all artists whose music is available locally..'''
    tracker = context.obj.tracker.client
    calliope.playlist.write(tracker.artists(), sys.stdout)


@tracker_cli.command(name='local-tracks')
@click.pass_context
def cmd_tracker_local_tracks(context):
    '''Show all tracks available locally..'''
    tracker = context.obj.tracker.client
    calliope.playlist.write(tracker.tracks(), sys.stdout)


@tracker_cli.command(name='scan')
@click.argument('path', nargs=1, type=click.Path(exists=True))
@click.pass_context
def cmd_tracker_scan(context, path):
    '''Scan all media files under a particular path and update a Tracker database.

    This is only possible when `--domain=app`.'''
    calliope.tracker.scan(context.obj.tracker, path)


@tracker_cli.command(name='search')
@click.argument('text', nargs=1, type=str)
@click.pass_context
def cmd_tracker_search(context, text):
    '''Search track titles in the Tracker database.'''
    tracker = context.obj.tracker.client
    calliope.playlist.write(tracker.tracks(track_search_text=text), sys.stdout)


@tracker_cli.command(name='sparql')
@click.argument('query', nargs=1, type=str)
@click.pass_context
def cmd_tracker_sparql(context, query):
    '''Execute a SPARQL query.'''
    calliope.tracker.execute_sparql(context.obj.tracker)


@tracker_cli.command(name='top-artists')
@click.pass_context
@click.option('-c', '--count', type=int, default=20,
              help="Maximum number of artists to return")
def cmd_tracker_top_artists(context, count):
    '''Query the top artists in a Tracker database'''
    tracker = context.obj.tracker_client
    result = list(tracker.artists_by_number_of_songs(limit=count))
    calliope.playlist.write(result, sys.stdout)


@cli.command(name='web')
@click.argument('playlist', type=click.File(mode='r'))
@click.pass_context
def cmd_web(context, playlist):
    '''Render a Calliope playlist to a web page'''
    text = calliope.web.render(calliope.playlist.read(playlist))
