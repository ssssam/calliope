#!/usr/bin/env python3
# Calliope
# Copyright (C) 2018  Sam Thursfield <sam@afuera.me.uk>
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

import logging
import sys

import calliope

log = logging.getLogger(__name__)


@calliope.cli.command(name='diff',
                      help="Compare multiple collections")
@click.argument('playlist1', type=click.File(mode='r'))
@click.argument('playlist2', type=click.File(mode='r'))
@click.pass_context
def cmd_diff(context, playlist1, playlist2):
    items1 = {item.id(): item for item in calliope.playlist.read(playlist1)}
    items2 = {item.id(): item for item in calliope.playlist.read(playlist2)}

    ids1 = set(items1.keys())
    ids2 = set(items2.keys())

    diff = sorted(ids1.difference(ids2))

    diff_items = [items1[i] for i in diff]

    calliope.playlist.write(diff_items, sys.stdout)
