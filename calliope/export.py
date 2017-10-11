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

'''calliope-export

Convert playlists and collections into different serialization formats.

'''

import argparse
import logging
import sys
import yaml

import calliope


def argument_parser():
    parser = argparse.ArgumentParser(
        description="Convert a Calliope playlist or collection into a "
                    "different format")
    parser.add_argument('playlist', nargs='*',
                        help="playlist file")
    parser.add_argument('-d', '--debug', action='store_true',
                        help="enable verbose debug output")
    parser.add_argument('-f', '--format', choices=['cue'], default='cue',
                        help="output format")

    return parser


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
        timestamp = item['start-time']
        output_text.append("  INDEX 01 %02i:%02i:00" % (int(timestamp / 60), int(timestamp % 60)))
    return '\n'.join(output_text)

def main():
    args = argument_parser().parse_args()

    if args.debug:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    if len(args.playlist) == 0:
        input_playlists = yaml.safe_load_all(sys.stdin)
    else:
        input_playlists = (yaml.safe_load(open(playlist, 'r'))
                           for playlist in args.playlist)

    if args.format == 'cue':
        for playlist_dict in input_playlists:
            print(convert_to_cue(calliope.Playlist(playlist_dict)))
    else:
        raise NotImplementedError("Unsupport format: %s" % args.format)


try:
    main()
except BrokenPipeError:
    # This happens when we're piped to `less` or something, it's harmless
    pass
except RuntimeError as e:
    sys.stderr.write("ERROR: %s\n" % e)
    sys.exit(1)
