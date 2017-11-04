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
import sys
import warnings

import calliope


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



@calliope.cli.command(name='spotify')
@click.option('-d', '--debug', is_flag=True)
@click.option('--user',
              help="show playlists for the given Spotify user")
def run(debug, user):
    '''Query user playlists from the Spotify streaming service'''

    if debug:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    client_id = calliope.config.get('spotify', 'client-id')
    client_secret = calliope.config.get('spotify', 'client-secret')
    redirect_uri = calliope.config.get('spotify', 'redirect-uri')

    if not user:
        user = calliope.config.get('spotify', 'user')
    if not user:
        raise RuntimeError("Please specify a username.")

    scope = ''
    try:
        token = util.prompt_for_user_token(user, scope, client_id=client_id,
                                           client_secret=client_secret,
                                           redirect_uri=redirect_uri)
    except spotipy.client.SpotifyException as e:
        raise RuntimeError(e)


    if not token:
        raise RuntimeError("No token")

    sp = spotipy.Spotify(auth=token)
    sp.trace = False
    playlists = sp.current_user_playlists()
    for playlist in playlists['items']:
        if playlist['owner']['id'] == user:
            tracks = sp.user_playlist_tracks(user, playlist_id=playlist['id'])
            print_spotify_playlist(playlist, tracks)
