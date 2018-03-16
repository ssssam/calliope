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


import click.testing

import calliope


class CliResult():
    def __init__(self, click_result):
        self.click_result = click_result
        self.exit_code = click_result.exit_code

    def assert_success(self):
        if self.click_result.exit_code != 0:
            raise AssertionError("Subprocess failed with code {}. Exception: {}. Output: {}".format(self.exit_code, self.click_result.exception, self.click_result.output))


class Cli():
    def __init__(self, prepend_args=[]):
        self.prepend_args = prepend_args

    def run(self, args, input=None):
        cli_runner = click.testing.CliRunner()
        result = cli_runner.invoke(calliope.cli, self.prepend_args + args, input=input)
        return CliResult(result)
