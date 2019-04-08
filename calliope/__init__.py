# Calliope
# Copyright (C) 2016,2018  Sam Thursfield <sam@afuera.me.uk>
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

'''Calliope is a set of tools for processing playlists.

This module contains the core parts of Calliope.

'''

import os

if os.environ.get('CALLIOPE_DOCS_BUILD') == 'yes':
    # When building the documentation, we stub out everything apart from the
    # Click CLI functions. This allows Sphinx plugins to run `import calliope`
    # without needing to have all of the dependencies available. We do this so
    # that we can use online documentation hosting at readthedocs.org.
    from . import cli
else:
    import click

    import copy
    import enum
    import json
    import logging
    import os
    import sys
    import urllib.parse


    def datadir():
        return os.path.join(os.path.dirname(__file__), 'data')


    def uri_to_path(uri):
        '''Convert a file:/// URI to a path.'''
        return urllib.parse.unquote(
            urllib.parse.urlsplit(uri).path)


    from . import cache
    from . import cli
    from . import config
    from . import playlist

    from . import diff
    from . import export
    from . import import_
    from . import shuffle
    from . import stat
    from . import sync


    # Some modules can be switched on/off using `meson configure` when Calliope
    # is installed from a Git checkout. This makes it possible to use some features
    # without having to install every possible dependency.
    #
    # In order to discover which modules we should import, Meson generates a .json
    # file which we read here. Normally the file is installed alongside the module,
    # but when running the test suite from the source tree, the file will be inside
    # the build/ dir and the testsuite sets the CALLIOPE_MODULES_CONFIG variable
    # accordingly.
    #
    # Note that we can't simply generate the __init__.py file using Meson because
    # this makes it impossible to do `import calliope` from inside the source tree,
    # which would make `meson test` unusable.

    def load_modules_config():
        if 'CALLIOPE_MODULES_CONFIG' in os.environ:
            modules_config_file = os.environ['CALLIOPE_MODULES_CONFIG']
        else:
            module_path = os.path.dirname(__file__)
            modules_config_file = os.path.join(module_path, 'modules.json')

        with open(modules_config_file) as f:
            return json.load(f)


    modules_config = load_modules_config()

    if modules_config['lastfm']:
        from . import lastfm

    if modules_config['musicbrainz']:
        from . import musicbrainz

    if modules_config['play']:
        from . import play

    if modules_config['spotify']:
        from . import spotify

    if modules_config['suggest']:
        from . import suggest

    if modules_config['tracker']:
        from . import tracker

    if modules_config['web']:
        from . import web
