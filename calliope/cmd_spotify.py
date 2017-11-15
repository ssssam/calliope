#!/usr/bin/env python3
# Calliope
# Copyright (C) 2017  Sam Thursfield <sam@afuera.me.uk>
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


import spotipy
import spotipy.util as util

import click
import yaml

import logging
import os
import sys
import warnings

import calliope


def flatten(l):
    return l[0] if len(l) == 1 else l


def annotate_track(sp, track_entry):
    '''Query Spotify-specific metadata about a track and add to its entry.'''
    logging.debug("Searching for track: %s", track_entry)
    result = sp.search(q=track_entry['track'], type='track')
    first_result = result['tracks']['items'][0]

    track_entry['spotify.artist'] = flatten([
        artist['name'] for artist in first_result['artists']
    ])
    if first_result['name'] != track_entry['track']:
        track_entry['spotify.track'] = first_result['name']
    track_entry['spotify.url'] = first_result['external_urls']['spotify']

    return track_entry


def print_spotify_playlist(playlist, tracks):
    print('---')
    print('name: %s' % playlist['name'])
    print('playlist:')
    for track in tracks['items']:
        print('- track: %s' % (track['track']['name']))

        artists = track['track']['artists']
        print('  artist: %s' % artists[0]['name'])

        location = track['track']['external_urls'].get('spotify')
        if location:
            print('  location: %s' % location)


@calliope.cli.group(name='spotify')
@click.option('--user',
              help="show playlists for the given Spotify user")
@click.pass_context
def spotify_cli(context, user):
    if not user:
        user = calliope.config.get('spotify', 'user')
    if not user:
        raise RuntimeError("Please specify a username.")

    context.obj.user = user

    if 'CALLIOPE_TEST_ONLY' in os.environ:
        sys.exit(0)

    client_id = calliope.config.get('spotify', 'client-id')
    client_secret = calliope.config.get('spotify', 'client-secret')
    redirect_uri = calliope.config.get('spotify', 'redirect-uri')

    scope = ''
    try:
        token = util.prompt_for_user_token(user, scope, client_id=client_id,
                                           client_secret=client_secret,
                                           redirect_uri=redirect_uri)
    except spotipy.client.SpotifyException as e:
        raise RuntimeError(e)

    if not token:
        raise RuntimeError("No token")

    context.obj.spotify = spotipy.Spotify(auth=token)
    context.obj.spotify.trace = False


@spotify_cli.command(name='annotate')
@click.argument('playlist', nargs=-1, type=click.Path(exists=True))
@click.pass_context
def cmd_annotate(context, playlist):
    '''Add Spotify-specific information to tracks in a playlist.'''
    sp = context.obj.spotify

    if len(playlist) == 0:
        input_playlists = yaml.safe_load_all(sys.stdin)
    else:
        input_playlists = (yaml.safe_load(open(p, 'r')) for p in playlist)
    input_playlists = [calliope.Playlist(p) for p in input_playlists]

    for playlist in input_playlists:
        for track in playlist:
            track = annotate_track(sp, track)
            print(track)


@spotify_cli.command(name='export')
@click.pass_context
def cmd_export(context):
    '''Query user playlists from Spotify'''
    sp = context.obj.spotify
    playlists = sp.current_user_playlists()
    for playlist in playlists['items']:
        if playlist['owner']['id'] == user:
            tracks = sp.user_playlist_tracks(user, playlist_id=playlist['id'])
            print_spotify_playlist(playlist, tracks)


@spotify_cli.command(name='import')
@click.pass_context
def cmd_import(context):
    '''Upload one or more playlists to Spotify'''
    raise NotImplementedError
