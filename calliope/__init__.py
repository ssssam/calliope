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

'''Calliope is a set of tools for processing playlists.

This module contains the core parts of Calliope.

'''

import click
import yaml

import copy
import enum
import logging
import os
import sys
import urllib.parse


def datadir():
    return os.path.join(os.path.dirname(__file__), 'data')


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


def uri_to_path(uri):
    '''Convert a file:/// URI to a path.'''
    return urllib.parse.unquote(
        urllib.parse.urlsplit(uri).path)


class OneShotResultsTable():
    '''A class for wrapping a generator that contains data.

    This is a way of returning a database cursor, without dumping it straight
    to stdout, and without reading the whole thing in to memory. The catch is
    that only one method which reads the cursor can ever be called, because we
    can't rewind the cursor afterwards.

    '''

    def __init__(self, headings, generator):
        '''Create a results table holder.

        The generator should return a single row for each call to next(). Each
        row should be a list of N elements, and there must also be N headings.

        '''
        self.headings = headings
        self.generator = generator
        self.dead = False

    def headings(self):
        return self.headings

    def display(self):
        '''Print the held data to stdout. Can only be called once.'''
        if self.dead:
            raise RuntimeError("Results table has already been used.")
        for row in self.generator:
            if len(row) != len(self.headings):
                warnings.warn("Number of columns doesn't match number of "
                              "headings!")
            print("\t".join(row))
        self.dead = True


from . import cache
from . import config
from . import playlist

from . import cmd_export
from . import cmd_import
from . import cmd_musicbrainz
from . import cmd_play
from . import cmd_shuffle
from . import cmd_spotify
from . import cmd_stat
from . import cmd_suggest
from . import cmd_sync
from . import cmd_tracker
from . import cmd_web
