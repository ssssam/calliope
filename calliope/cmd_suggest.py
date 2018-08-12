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

'''calliope-suggest

Recommend playlist entries or annotations based on existing ones.

Uses the LightFM recommendation library. For more information on LightFM
see its documentation at: http://lyst.github.io/lightfm/docs/home.html
'''

import click
import lightfm
import numpy
import yaml

import os
import sys

import calliope


@calliope.cli.group(name='suggest',
                    help="Suggest items or annotations")
@click.pass_context
def suggest_cli(context):
    pass

@suggest_cli.command(name='tracks')
@click.option('--from', 'from_', required=True, type=click.Path(exists=True),
              help="collection from which tracks should be suggested")
@click.option('--count', type=int, default=10,
              help="number of track suggestions to generate")
@click.option('--training-input', multiple=True,
              type=(click.Path(exists=True), float),
              help="a collection or playlist used to train the recommender. "
                   "A training input requires two arguments, the first is the "
                   "path to the file, the second is how it should weight the "
                   "training. Weight should be a value between -1.0 and 1.0, "
                   "where 1.0 is the most positive weighting and -1.0 the "
                   "most negative.")
@click.pass_context
def tracks(context, from_, count, training_input):
    '''Suggest tracks from a collection based on the given training inputs.'''

    # First we need a 'user-item' interaction matrix. Each 'item' is a track in
    # the input collection. Each 'user' is one of the input playlists.

    input_collection = calliope.Playlist(yaml.safe_load(open(from_, 'r')))

    interaction_matrix = []

    for path, weight in training_input:
        input_playlists = [calliope.Playlist(data) for data in yaml.safe_load_all(open(path, 'r'))]

        # Set all interactions to zeros
        interaction_list = [0.0] * input_collection.track_count()

        for input_playlist in input_playlists:
            for track in input_playlist.tracks():
                track_id = input_collection.track_index(track)
                if track_id:
                    interaction_list[track_id] = weight
        interaction_matrix.append(interaction_list)

    interaction_matrix = numpy.matrix(interaction_matrix)
    print(interaction_matrix)
