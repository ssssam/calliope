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


import pytest

import calliope

import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import traceback

import calliope


class Result():

    def __init__(self,
                 exit_code=None,
                 output=None,
                 stderr=None):
        self.exit_code = exit_code
        self.output = output
        self.stderr = stderr

    def assert_success(self, fail_message=''):
        assert self.exit_code == 0, fail_message

    def json(self):
        return [json.loads(line) for line in self.output.strip().split('\n')]


class Cli():
    def __init__(self, prepend_args=[]):
        self.prepend_args = prepend_args

    def run(self, args, input=None):
        result = self.invoke(calliope.cli, self.prepend_args + args, input=input)

        command = "cpe " + " ".join(args)
        print("Calliope exited with code {} for invocation:\n\t{}"
                .format(result.exit_code, command))
        if result.stderr:
            print("Program stderr was:\n{}".format(result.stderr))

        return result

    def invoke(self, cli, args=None, input=None):
        result = subprocess.run(
            [sys.executable, '-m', 'calliope'] + args, encoding='utf8',
            input=input, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        return Result(exit_code=result.returncode,
                      output=result.stdout,
                      stderr=result.stderr)
