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

import logging
import sys
import yaml

import calliope


def convert_to_cue(playlist):
    if playlist.kind != calliope.PlaylistKind.PLAYLIST:
        raise RuntimeError("Only playlists can be converted to CUE sheets")

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


@calliope.cli.command(name='export')
@click.option('-d', '--debug', is_flag=True)
@click.option('-f', '--format', type=click.Choice(['cue']), default='cue')
@click.argument('playlist', nargs=-1, type=click.Path(exists=True))
def run(debug, format, playlist):
    '''Convert to a different playlist format'''
    if debug:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    if len(playlist) == 0:
        input_playlists = yaml.safe_load_all(sys.stdin)
    else:
        input_playlists = (yaml.safe_load(open(p, 'r')) for p in playlist)

    if format == 'cue':
        for playlist_dict in input_playlists:
            print(convert_to_cue(calliope.Playlist(playlist_dict)))
    else:
        raise NotImplementedError("Unsupport format: %s" % format)
