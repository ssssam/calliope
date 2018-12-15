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
import urllib.request

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

    def create(artist, title, album=None, tracknumber=None):
        filename = '{} - {}.ogg'.format(artist, title)
        path = tmpdir.join('musicdir', filename)
        shutil.copy(template_path, path)

        template = mutagen.oggvorbis.OggVorbis(path)
        template.tags['PERFORMER'] = artist
        template.tags['TITLE'] = title
        if album:
            template.tags['ALBUM'] = album
        if tracknumber:
            template.tags['TRACKNUMBER'] = str(tracknumber)
        template.save()

    create('Artist 1', 'Track 1', album='Album 1', tracknumber=1)
    create('Artist 1', 'Track 2', album='Album 1', tracknumber=2)
    create('Artist 1', 'Track 3')
    create('Artist 2', 'Track 1')
    create('Artist 2', 'Track 2')
    create('Artist 2', 'Track 3')

    return str(tmpdir.join('musicdir'))


def test_annotate_locations(tracker_cli, tmpdir, musicdir):
    result = tracker_cli.run(['scan', musicdir])
    result.assert_success()

    input_playlist = [
        {
            'artist': 'Artist 1',
            'track': 'Track 1',
        }
    ]

    result = tracker_cli.run(['annotate', '-'], input_playlist=input_playlist)
    result.assert_success()

    expected_url = 'file://' + urllib.request.pathname2url(os.path.join(musicdir, 'Artist 1 - Track 1.ogg'))

    output_playlist = result.json()
    assert output_playlist[0]['artist'] == 'Artist 1'
    assert output_playlist[0]['track'] == 'Track 1'
    assert output_playlist[0]['tracker.url'] == expected_url


def test_expand_tracks_for_artist(tracker_cli, tmpdir, musicdir):
    result = tracker_cli.run(['scan', musicdir])
    result.assert_success()

    input_playlist = [
        {
            'artist': 'Artist 1',
            'track': 'Track 1',
        },
        {
            'artist': 'Artist 2',
        }
    ]

    result = tracker_cli.run(['expand-tracks', '-'], input_playlist=input_playlist)
    result.assert_success()

    output_playlist = result.json()
    assert output_playlist[0]['artist'] == 'Artist 1'
    assert output_playlist[0]['track'] == 'Track 1'
    assert output_playlist[1]['artist'] == 'Artist 2'
    assert output_playlist[1]['track'] == 'Track 1'
    assert output_playlist[2]['artist'] == 'Artist 2'
    assert output_playlist[2]['track'] == 'Track 2'
    assert output_playlist[3]['artist'] == 'Artist 2'
    assert output_playlist[3]['track'] == 'Track 3'
    assert len(output_playlist) == 4


def test_expand_tracks_for_album(tracker_cli, tmpdir, musicdir):
    result = tracker_cli.run(['scan', musicdir])
    result.assert_success()

    input_playlist = [
        {
            'artist': 'Artist 1',
            'album': 'Album 1',
        },
    ]

    result = tracker_cli.run(['expand-tracks', '-'], input_playlist=input_playlist)
    result.assert_success()

    output_playlist = result.json()
    assert output_playlist[0]['artist'] == 'Artist 1'
    assert output_playlist[0]['track'] == 'Track 1'
    assert output_playlist[1]['artist'] == 'Artist 1'
    assert output_playlist[1]['track'] == 'Track 2'
    assert len(output_playlist) == 2


def test_scan_show(tracker_cli, tmpdir, musicdir):
    result = tracker_cli.run(['scan', musicdir])
    result.assert_success()

    result = tracker_cli.run(['local-albums'])
    result.assert_success()

    collection = result.json()
    assert collection[0]['artist'] == 'Artist 1'
    assert collection[0]['tracks'][0]['track'] == 'Track 1'
    assert collection[0]['tracks'][1]['track'] == 'Track 2'
    assert collection[1]['artist'] == 'Artist 1'
    assert collection[1]['tracks'][0]['track'] == 'Track 3'
    assert collection[2]['artist'] == 'Artist 2'
    assert collection[2]['tracks'][0]['track'] == 'Track 1'
    assert collection[2]['tracks'][1]['track'] == 'Track 2'
    assert collection[2]['tracks'][2]['track'] == 'Track 3'

    result = tracker_cli.run(['local-tracks'])
    result.assert_success()

    collection = result.json()
    assert collection[0]['artist'] == 'Artist 1'
    assert collection[0]['track'] == 'Track 1'
    assert collection[1]['artist'] == 'Artist 2'
    assert collection[1]['track'] == 'Track 1'
    assert collection[2]['artist'] == 'Artist 1'
    assert collection[2]['track'] == 'Track 2'
    assert collection[3]['artist'] == 'Artist 2'
    assert collection[3]['track'] == 'Track 2'
    assert collection[4]['artist'] == 'Artist 1'
    assert collection[4]['track'] == 'Track 3'
    assert collection[5]['artist'] == 'Artist 2'
    assert collection[5]['track'] == 'Track 3'
