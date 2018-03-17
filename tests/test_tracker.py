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


import mutagen.oggvorbis
import pytest

import os
import shutil

import testutils


@pytest.fixture()
def tracker_cli(tmpdir):
    '''Fixture for testing through the `cpe` commandline interface.'''
    return testutils.Cli(prepend_args=['--debug', 'tracker', '--app-domain-dir', tmpdir])


@pytest.fixture()
def musicdir(tmpdir):
    '''Fixture providing a standard set of tagged audio files.'''
    template_path = os.path.join(os.path.dirname(__file__), 'data', 'empty.ogg')
    tmpdir.ensure('musicdir', dir=True)

    for artist in ['Artist 1', 'Artist 2']:
        for track in ['Track 1', 'Track 2', 'Track 3']:
            filename = '{} - {}.ogg'.format(artist, track)
            path = tmpdir.join('musicdir', filename)
            shutil.copy(template_path, path)

            template = mutagen.oggvorbis.OggVorbis(path)
            template.tags['PERFORMER'] = artist
            template.tags['TITLE'] = track
            template.save()

    return str(tmpdir.join('musicdir'))


def test_scan_show(tracker_cli, tmpdir, musicdir):
    result = tracker_cli.run(['scan', musicdir])
    result.assert_success()

    result = tracker_cli.run(['show'])
    result.assert_success()
    assert result.output.startswith('collection:')
