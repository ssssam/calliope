# Calliope
# Copyright (C) 2017  Sam Thursfield <sam@afuera.me.uk>
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


import click.testing
import pytest

import calliope


class Cli():
    def run(self, args, input=None):
        cli_runner = click.testing.CliRunner()
        result = cli_runner.invoke(calliope.cli, args, input=input)
        return result


@pytest.fixture()
def cli():
    '''Fixture for testing through the `cpe` commandline interface.'''
    return Cli()


def test_export(cli):
    result = cli.run(['export'])
    assert result.exit_code == 0


def test_import(cli):
    example_pls = '''[playlist]
    NumberOfEntries=0
    '''

    result = cli.run(['import'], input=example_pls)
    assert result.exit_code == 0


def test_play(cli):
    result = cli.run(['play', '--output', '/dev/null'])
    assert result.exit_code == 0


def test_spotify(cli):
    result = cli.run(['spotify'])
    assert result.exit_code == 0


def test_stat(cli):
    result = cli.run(['stat'])
    assert result.exit_code == 0


def test_sync(cli):
    result = cli.run(['sync'])
    assert result.exit_code == 0


def test_tracker(cli):
    result = cli.run(['tracker'])
    assert result.exit_code == 0