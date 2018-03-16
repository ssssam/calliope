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
import os
import shutil
import subprocess
import sys
import traceback

# We use pytest internals to capture the stdout/stderr during
# a run of the Calliope CLI. We do this because click's
# CliRunner convenience API (click.testing module) does not support
# separation of stdout/stderr and also breaks the 'trackerappdomain' lib.
#
from _pytest.capture import MultiCapture, FDCapture

import calliope


class Result():

    def __init__(self,
                 exit_code=None,
                 exception=None,
                 exc_info=None,
                 output=None,
                 stderr=None):
        self.exit_code = exit_code
        self.exc = exception
        self.exc_info = exc_info
        self.output = output
        self.stderr = stderr

    def assert_success(self, fail_message=''):
        assert self.exit_code == 0, fail_message
        assert self.exc is None, fail_message


class Cli():
    def __init__(self, prepend_args=[]):
        self.prepend_args = prepend_args

    def run(self, args, input=None):
        result = self.invoke(calliope.cli, self.prepend_args + args, input=input)

        command = "cpe " + " ".join(args)
        print("Calliope exited with code {} for invocation:\n\t{}"
                .format(result.exit_code, command))
        if result.output:
            print("Program output was:\n{}".format(result.output))
        if result.stderr:
            print("Program stderr was:\n{}".format(result.stderr))

            if result.exc_info and result.exc_info[0] != SystemExit:
                traceback.print_exception(*result.exc_info)

        return result

    @contextlib.contextmanager
    def setup_input(self, text):
        if text:
            yield io.StringIO(text)
        else:
            with open(os.devnull) as devnull:
                yield devnull

    def invoke(self, cli, args=None, input=None):
        exc_info = None
        exception = None
        exit_code = 0

        # Temporarily redirect sys.stdin to /dev/null to ensure that
        # Popen doesn't attempt to read pytest's dummy stdin.
        old_stdin = sys.stdin
        with self.setup_input(text=input) as input_stream:
            sys.stdin = input_stream

            capture = MultiCapture(out=True, err=True, in_=False, Capture=FDCapture)
            capture.start_capturing()

            try:
                cli.main(args=args or (), prog_name=cli.name)
            except SystemExit as e:
                if e.code != 0:
                    exception = e

                exc_info = sys.exc_info()

                exit_code = e.code
                if not isinstance(exit_code, int):
                    sys.stdout.write('Program exit code was not an integer: ')
                    sys.stdout.write(str(exit_code))
                    sys.stdout.write('\n')
                    exit_code = 1
            except Exception as e:
                exception = e
                exit_code = -1
                exc_info = sys.exc_info()
            finally:
                sys.stdout.flush()

        sys.stdin = old_stdin
        out, err = capture.readouterr()
        capture.stop_capturing()

        return Result(exit_code=exit_code,
                      exception=exception,
                      exc_info=exc_info,
                      output=out,
                      stderr=err)
