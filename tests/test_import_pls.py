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


import io
import json

import calliope


example_1 = """
[playlist]
NumberOfEntries=2
File1=file:///media/Music/Song%201.mp3
Title1=Song 1
File2=file:///media/Music/Song%202.mp3
Title2=Song 2
"""


def test_basic(cli):
    result = cli.run(['import', '-'], input=example_1)

    assert result.exit_code == 0

    items = list(calliope.playlist.read(io.BytesIO(result.output.encode('utf-8'))))

    assert items == [
        {'location': 'file:///media/Music/Song%201.mp3', 'track': 'Song 1'},
        {'location': 'file:///media/Music/Song%202.mp3', 'track': 'Song 2'},
    ]
