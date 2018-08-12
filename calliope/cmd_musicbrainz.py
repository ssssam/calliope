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

import click
import musicbrainzngs
import yaml

import logging
import sys
import warnings

import calliope


# FIXME: we need to cache requests and responses.
# How about
# https://github.com/jaraco/jaraco.net/blob/master/jaraco/net/http/caching.py ?

def add_musicbrainz_artist(item):
    artist = item['artist']
    result = musicbrainzngs.search_artists(artist=artist)['artist-list']
    if len(result) == 0:
        print("# Unable to find %s on musicbrainz" % artist)
    else:
        artist = result[0]
        item['musicbrainz.artist'] = artist['id']
        if 'country' in artist:
            item['musicbrainz.artist.country'] = artist['country']
    return item


@calliope.cli.command(name='musicbrainz')
@click.argument('playlist', nargs=-1, type=click.Path(exists=True))
@click.pass_context
def run(context, playlist):
    '''Annotate playlists with data from Musicbrainz'''

    musicbrainzngs.set_useragent("Calliope", "0.1", "https://github.com/ssssam/calliope")

    if len(playlist) == 0:
        input_playlists = yaml.safe_load_all(sys.stdin)
    else:
        input_playlists = (yaml.safe_load(open(p, 'r')) for p in playlist)

    # FIXME: should be a collection if any inputs are collections, otherwise a
    # playlist
    print('collection:')
    for playlist_data in input_playlists:
        for item in calliope.Playlist(playlist_data):
            if 'artist' in item and 'musicbrainz.artist' not in item:
                try:
                    print(add_musicbrainz_artist(item))
                except RuntimeError as e:
                    raise RuntimeError("%s\nItem: %s" % (e, item))
