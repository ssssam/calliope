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

import os
import sys

import calliope


def suggest_tracks(corpus_playlist, count, training_input):
    corpus_tracks = [item.tracks() for item in corpus_playlist]

    interaction_matrix = []

    for playlist_stream, weight in training_input:
        # Set all interactions to zeros
        interaction_list = [0.0] * corpus_tracks

        for item in playlist_stream:
            for track in item.tracks():
                track_index = corpus_tracks.index(track)
                if track_id:
                    interaction_list[track_id] = weight
        interaction_matrix.append(interaction_list)

    interaction_matrix = numpy.matrix(interaction_matrix)
    print(interaction_matrix)
