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


import click

import argparse
import os
import sys
import urllib.parse
import warnings

import calliope


def measure_size(playlist):
    '''Measure the total size of the files listed.'''
    def measure_one(item):
        path = urllib.parse.unquote(urllib.parse.urlsplit(item['location']).path)
        try:
            return os.stat(path).st_size
        except FileNotFoundError as e:
            warnings.warn("Did not find file %s" % path)
            return 0

    size = 0
    for item in playlist:
        if 'location' in item:
            size += measure_one(item)
        elif 'tracks' in item:
            for track in item['tracks']:
                if 'location' in track:
                    size += measure_one(track)
    print("Total size: %i MB" % (size / 1024 / 1024.0))


@calliope.cli.command(name='stat')
@click.option('--size', '-s', is_flag=True,
              help="show the total size on disk of the playlist contents")
@click.argument('playlist', type=click.File(mode='r'))
@click.pass_context
def run(context, size, playlist):
    '''Information about the contents of a playlist'''

    input_playlist = list(calliope.playlist.read(playlist))

    if size:
        measure_size(input_playlist)
    else:
        print("Please select a mode.")
