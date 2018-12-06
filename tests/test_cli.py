# Calliope
# Copyright (C) 2017-2018  Sam Thursfield <sam@afuera.me.uk>
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


import mock
import os


# Note that these tests do not run Calliope in-process, they spawn a subprocess.
# This is because trackerappdomain breaks if you run it multiple times in a
# single process.


def test_musicbrainz(cli):
    result = cli.run(['musicbrainz', '-'], input='')
    assert result.exit_code == 0


def test_play(cli):
    result = cli.run(['play', '-', '--output', '/dev/null'])
    assert result.exit_code == 0


def test_shuffle(cli):
    result = cli.run(['shuffle', '-'])
    assert result.exit_code == 0


def test_spotify(cli):
    os.environ['CALLIOPE_SPOTIFY_MOCK'] = 'yes'
    result = cli.run(['--debug' ,'spotify'])
    assert result.exit_code == 0
    result = cli.run(['--debug', 'spotify', '--user', '__calliope_tests', 'annotate', '-'], input='')
    assert result.exit_code == 0
    result = cli.run(['--debug', 'spotify', '--user', '__calliope_tests', 'export'])
    assert result.exit_code == 0


def test_stat(cli):
    result = cli.run(['stat', '-'])
    assert result.exit_code == 0


def test_suggest(cli):
    result = cli.run(['suggest'])
    assert result.exit_code == 0


def test_sync(cli):
    result = cli.run(['sync', '-'])
    assert result.exit_code == 0


def test_tracker(cli):
    result = cli.run(['tracker'])
    assert result.exit_code == 0


def test_web(cli):
    result = cli.run(['web', '-'])
    assert result.exit_code == 0
