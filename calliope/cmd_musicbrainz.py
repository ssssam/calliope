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

log = logging.getLogger(__name__)


def add_musicbrainz_artist(cache, item):
    artist_name = item['artist']

    found, entry = cache.lookup('artist:{}'.format(artist_name))

    if found:
        log.debug("Found artist:{} in cache".format(artist_name))
    else:
        log.debug("Didn't find artist:{} in cache, running remote query".format(artist_name))
        result = musicbrainzngs.search_artists(artist=artist_name)['artist-list']
        if len(result) == 0:
            entry = None
        else:
            entry = result[0]

        cache.store('artist:{}'.format(artist_name), entry)

    if entry is None:
        print("# Unable to find %s on musicbrainz" % artist_name)
    else:
        item['musicbrainz.artist'] = entry['id']
        if 'country' in entry:
            item['musicbrainz.artist.country'] = entry['country']

    return item


@calliope.cli.command(name='musicbrainz')
@click.argument('playlist', type=click.File(mode='r'))
@click.pass_context
def run(context, playlist):
    '''Annotate playlists with data from Musicbrainz'''

    cache = calliope.cache.Cache(namespace='musicbrainz')

    musicbrainzngs.set_useragent("Calliope", "0.1", "https://github.com/ssssam/calliope")

    output_playlist = []

    for item in calliope.playlist.read(playlist):
        if 'artist' in item and 'musicbrainz.artist' not in item:
            try:
                output_playlist.append(add_musicbrainz_artist(cache, item))
            except RuntimeError as e:
                raise RuntimeError("%s\nItem: %s" % (e, item))

    calliope.playlist.write(output_playlist, sys.stdout)
