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


class SpotifyContext():
    def __init__(self, user):
        if not user:
            user = calliope.config.get('spotify', 'user')
        if not user:
            raise RuntimeError("Please specify a username.")

        self.user = user
        log.debug("Spotify user: {}".format(user))

    def authenticate(self, token=None):
        if not token:
            client_id = calliope.config.get('spotify', 'client-id')
            client_secret = calliope.config.get('spotify', 'client-secret')
            redirect_uri = calliope.config.get('spotify', 'redirect-uri')

            scope = 'user-top-read'
            try:
                token = util.prompt_for_user_token(
                    self.user, scope, client_id=client_id,
                    client_secret=client_secret, redirect_uri=redirect_uri)
            except spotipy.client.SpotifyException as e:
                raise RuntimeError(e)

        if not token:
            raise RuntimeError("No token")

        log.debug("Spotify access token: {}".format(token))
        self.api = spotipy.Spotify(auth=token)
        self.api.trace = False


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

def export(spotify):
    sp = spotify.api
    user = spotify.user

    playlists = sp.current_user_playlists()
    for playlist in playlists['items']:
        if playlist['owner']['id'] == user:
            tracks = sp.user_playlist_tracks(user, playlist_id=playlist['id'])
            print_spotify_playlist(playlist, tracks)


def top_artists(spotify, count, time_range):
    sp = spotify.api
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

    return output
