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


import sys
import warnings

import calliope.cli

def pretty_warnings(message, category, filename, lineno,
                    file=None, line=None):
    return 'WARNING: %s\n' % (message)

warnings.formatwarning = pretty_warnings


try:
    calliope.cli.cli()
except RuntimeError as e:
    sys.stderr.write("ERROR: %s\n" % e)
    sys.exit(1)
except BrokenPipeError as e:
    # These happen when we are piped to `less` or something and are harmless.
    sys.exit(0)
