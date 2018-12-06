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

import argparse
import copy
import itertools
import os
import random
import sys
import urllib.parse
import warnings

import calliope


def measure_size(playlists):
    '''Measure the total size of the files listed.'''
    def measure_one(item):
        path = urllib.parse.unquote(urllib.parse.urlsplit(item['location']).path)
        try:
            return os.stat(path).st_size
        except FileNotFoundError as e:
            warnings.warn("Did not find file %s" % path)
            return 0

    size = 0
    for playlist_data in playlists:
        for item in calliope.playlist.Playlist(playlist_data):
            if 'location' in item:
                size += measure_one(item)
            elif 'tracks' in item:
                for track in item['tracks']:
                    if 'location' in track:
                        size += measure_one(track)
    print("Total size: %i MB" % (size / 1024 / 1024.0))


def shuffle(playlist, count):
    # This is the simplest shuffle that we could implement.
    #
    # There is a lot more involved in creating "good" shuffled playlists. For
    # example see https://labs.spotify.com/2014/02/28/how-to-shuffle-songs/
    corpus = copy.copy(list(playlist))
    random.shuffle(corpus)
    if count:
        corpus = corpus.items[0:count]

    return corpus
