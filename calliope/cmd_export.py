#!/usr/bin/env python3
# Calliope
# Copyright (C) 2016,2018  Sam Thursfield <sam@afuera.me.uk>
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

import sys

import calliope


def convert_to_cue(playlist):
    output_text = ['FILE "none" WAVE']
    for i, item in enumerate(playlist):
        output_text.append("  TRACK %02i AUDIO" % (i + 1))
        if 'track' in item:
            output_text.append("    TITLE \"%s\"" % item['track'])
        if 'artist' in item:
            output_text.append("    PERFORMER \"%s\"" % item['artist'])
        if 'start-time' in item:
            timestamp = item['start-time']
        else:
            if i == 0:
                timestamp = 0
            else:
                raise RuntimeError("The 'start-time' field must be set for all entries "
                                   "in order to create a CUE sheet")
        output_text.append("  INDEX 01 %02i:%02i:00" % (int(timestamp / 60), int(timestamp % 60)))
    return '\n'.join(output_text)


def convert_to_m3u(playlist):
    output_text = []
    for i, item in enumerate(playlist):
        if 'url' in item:
            output_text.append(item['url'])
        else:
            raise RuntimeError("The 'url' field must be set for all entries "
                                "in order to create an M3U playlist")
    return '\n'.join(output_text)


@calliope.cli.command(name='export')
@click.option('-f', '--format', type=click.Choice(['cue', 'm3u']), default='m3u')
@click.argument('playlist', nargs=1, type=click.File('r'))
@click.pass_context
def run(context, format, playlist):
    '''Convert to a different playlist format'''

    if format == 'cue':
        print(convert_to_cue(calliope.playlist.read(playlist)))
    elif format == 'm3u':
        print(convert_to_m3u(calliope.playlist.read(playlist)))
    else:
        raise NotImplementedError("Unsupport format: %s" % format)
