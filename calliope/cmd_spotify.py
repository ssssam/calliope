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

import logging
import os
import sys
import warnings

import calliope

log = logging.getLogger(__name__)


def flatten(l):
    return l[0] if len(l) == 1 else l


def annotate_track(sp, track_entry):
    '''Query Spotify-specific metadata about a track and add to its entry.'''
    log.debug("Searching for track: %s", track_entry)
    result = sp.search(q=track_entry['track'], type='track')

    if len(result['tracks']['items']) > 0:
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


@calliope.cli.group(name='spotify',
                    help="Interface to the Spotify online streaming service")
@click.option('--token',
              help="use the given API access token")
@click.option('--user',
              help="show playlists for the given Spotify user")
@click.pass_context
def spotify_cli(context, token, user):
    if not user:
        user = calliope.config.get('spotify', 'user')
    if not user:
        raise RuntimeError("Please specify a username.")

    context.obj.user = user
    log.debug("Spotify user: {}".format(user))

    if 'CALLIOPE_TEST_ONLY' in os.environ:
        sys.exit(0)

    if not token:
        client_id = calliope.config.get('spotify', 'client-id')
        client_secret = calliope.config.get('spotify', 'client-secret')
        redirect_uri = calliope.config.get('spotify', 'redirect-uri')

        scope = 'user-top-read'
        try:
            token = util.prompt_for_user_token(user, scope, client_id=client_id,
                                            client_secret=client_secret,
                                            redirect_uri=redirect_uri)
        except spotipy.client.SpotifyException as e:
            raise RuntimeError(e)

    if not token:
        raise RuntimeError("No token")

    log.debug("Spotify access token: {}".format(token))
    context.obj.spotify = spotipy.Spotify(auth=token)
    context.obj.spotify.trace = False


@spotify_cli.command(name='annotate')
@click.argument('playlist', type=click.File(mode='r'))
@click.pass_context
def cmd_annotate(context, playlist):
    '''Add Spotify-specific information to tracks in a playlist.'''
    sp = context.obj.spotify

    for track in calliope.playlist.read(playlist):
        track = annotate_track(sp, track)
        calliope.playlist.write([track], sys.stdout)


@spotify_cli.command(name='export')
@click.pass_context
def cmd_export(context):
    '''Query user playlists from Spotify'''
    sp = context.obj.spotify
    user = context.obj.user
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


@spotify_cli.command(name='top-artists')
@click.pass_context
@click.option('-c', '--count', type=int, default=20,
              help="Maximum number of artists to return")
@click.option('--time-range', default='long_term',
              type=click.Choice(['short_term', 'medium_term', 'long_term']))
def cmd_top_artists(context, count, time_range):
    '''Return user's top artists.'''
    sp = context.obj.spotify
    response = sp.current_user_top_artists(limit=count, time_range=time_range)['items']

    if count > 50:
        # This is true as of 2018-08-18; see:
        # https://developer.spotify.com/documentation/web-api/reference/personalization/get-users-top-artists-and-tracks/
        raise RuntimeError("Requested {} top artists, but the Spotify API will "
                           "not return more than 50.".format(count))

    output = []
    for i, artist_info in enumerate(response):
        output_item = {
            'artist': artist_info['name'],
            'spotify.id': artist_info['id'],
            'spotify.user-ranking': i+1,
            'spotify.artist-image': artist_info['images']
        }
        output.append(output_item)

    calliope.playlist.write(output, sys.stdout)
