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


import json


def test_export_cue(cli):
    input_tracks = [
        { 'artist': 'Test1', 'start-time': 0 },
        { 'artist': 'Test2', 'start-time': 50 }
    ]

    expected_output = '\n'.join([
        "FILE \"none\" WAVE",
        "  TRACK 01 AUDIO",
        "    PERFORMER \"Test1\"",
        "  INDEX 01 00:00:00",
        "  TRACK 02 AUDIO",
        "    PERFORMER \"Test2\"",
        "  INDEX 01 00:50:00"])

    result = cli.run(['export', '--format=cue', '-'], input='\n'.join(json.dumps(track) for track in input_tracks))

    assert result.exit_code == 0
    assert result.output.strip() == expected_output


def test_export_m3u(cli):
    input_tracks = [
        { 'artist': 'Test1', 'location': 'file:///test1' },
        { 'artist': 'Test2', 'location': 'file:///test2' }
    ]

    expected_output = '\n'.join([
        "file:///test1",
        "file:///test2"
    ])

    result = cli.run(['export', '--format=m3u', '-'], input='\n'.join(json.dumps(track) for track in input_tracks))

    assert result.exit_code == 0
    assert result.output.strip() == expected_output
