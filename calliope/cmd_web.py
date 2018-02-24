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
import jinja2
import yaml

import argparse
import logging
import os
import sys

import calliope


def render_html(playlists, template_filename):
    '''Render a playlist as HTML using a template.'''

    with open(template_filename, 'r') as f:
        template = jinja2.Template(f.read())

    #file_uris = []
    #for playlist_data in playlists:
        #for item in calliope.Playlist(playlist_data):
            #print(item)

    return template.render()


@calliope.cli.command(name='web')
@click.argument('playlist', nargs=-1, type=click.Path(exists=True))
@click.pass_context
def run(context, playlist):
    '''Render a Calliope playlist to a web page'''

    if len(playlist) == 0:
        input_playlists = yaml.safe_load_all(sys.stdin)
    else:
        input_playlists = (yaml.safe_load(open(p, 'r')) for p in playlist)

    template = os.path.join(calliope.datadir(), 'web', 'templates', 'playlist.html.in')

    text = render_html(input_playlists, template)
    print(text)
