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

'''calliope-import

Convert playlists and collections from different serialization formats.

'''

import click

import configparser
import logging
import sys

import calliope

log = logging.getLogger(__name__)


def guess_format(text):
    try:
        log.debug("guess_format: Checking .pls format")
        parser = configparser.ConfigParser()
        parser.read_string(text)
        if parser.has_section('playlist'):
            return 'pls'
    except (UnicodeDecodeError, configparser.Error) as e:
        log.debug("guess_format: Got exception: %s", e)
        pass
    return None


def parse_pls(text):
    parser = configparser.ConfigParser(interpolation=None)
    parser.read_string(text)
    number_of_entries = parser.getint('playlist', 'NumberOfEntries')

    entries = []
    for i in range(1, number_of_entries+1):
        entry = {
            'location': parser.get('playlist', 'File%i' % i),
            'track': parser.get('playlist', 'Title%i' % i)
        }
        entries.append(calliope.playlist.Item(entry))
    return entries

def import_(text):
    playlist_format = guess_format(text)
    if not playlist_format:
        raise RuntimeError("Could not determine the input format.")
    elif playlist_format == 'pls':
        entries = parse_pls(text)
    return entries