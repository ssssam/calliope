# Calliope
# Copyright (C) 2016  Sam Thursfield <sam@afuera.me.uk>
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

'''calliope-sync'''


import click

import itertools
import logging
import os
import string
import subprocess
import sys
import warnings

import calliope

log = logging.getLogger(__name__)


class Operation():
    '''Base class for operations that this tool can perform.'''
    pass


class TranscodeToMP3Operation(Operation):
    '''Represesents transcoding to MP3 using GStreamer.'''
    def __init__(self, source_path, dest_path):
        self.source_path, self.dest_path = source_path, dest_path

    def __str__(self):
        return ('gst-launch-1.0 -t filesrc location="%s" ! decodebin ! '
                'audioconvert ! lamemp3enc quality=0 ! id3mux ! '
                'filesink location="%s"' % (self.source_path, self.dest_path))

    def run(self):
        if not os.path.exists(os.path.dirname(self.dest_path)):
            os.makedirs(os.path.dirname(self.dest_path))
        if not os.path.exists(self.dest_path):
            subprocess.check_call(['gst-launch-1.0', '-t', 'filesrc',
                                   'location="%s"' % self.source_path, '!',
                                   'decodebin', '!', 'audioconvert', '!',
                                   'lamemp3enc', 'quality=0', '!', 'id3mux', '!'
                                   'filesink', 'location="%s"' % self.dest_path])


class CopyOperation(Operation):
    '''Represents a simple file copy.'''
    def __init__(self, source_path, dest_path):
        self.source_path, self.dest_path = source_path, dest_path

    def __str__(self):
        return 'rsync --archive %s %s' % (self.source_path, self.dest_path)

    def run(self):
        if not os.path.exists(os.path.dirname(self.dest_path)):
            os.makedirs(os.path.dirname(self.dest_path))
        if not os.path.exists(self.dest_path):
            subprocess.check_call(['rsync', '--times', self.source_path, self.dest_path])


def ensure_number(filename, number):
    '''Ensure filename begins with 'number'.'''
    existing_number = ''.join(itertools.takewhile(str.isdigit, filename))
    if len(existing_number) == 0 or str(existing_number) != str(number):
        return '%03i_%s' % (number, filename)
    else:
        return filename


def make_dirname(*items):
    return '_'.join(filter(None, items))


def sync_track(location, target, allow_formats=['all'], target_dirname=None,
               target_filename=None):
    path = calliope.uri_to_path(location)

    # We only look at the filename to determine file format, which is the
    # quickest method but not the most reliable.
    filetype = os.path.splitext(path)[1].lstrip('.')

    if target_dirname:
        target_dirname = os.path.join(target, target_dirname)
    else:
        target_dirname = target
    if not target_filename:
        target_filename = os.path.basename(path)

    if 'all' in allow_formats or filetype in allow_formats:
        sync_operation = CopyOperation(path, os.path.join(target_dirname, target_filename))
    else:
        if 'mp3' not in allow_formats:
            raise NotImplementedError(
                "File %s needs to be transcoded to an allowed format, but "
                "only transcoding to MP3 is supported right now, and MP3 "
                "doesn't seem to be allowed. Please allow MP3 files, or "
                "improve this tool." % target_filename)
        else:
            if not target_filename.endswith('.mp3'):
                target_filebasename = os.path.splitext(target_filename)[0]
                target_filename = target_filebasename + '.mp3'
            sync_operation = TranscodeToMP3Operation(path, os.path.join(target_dirname,
                                                                        target_filename))
    return sync_operation


def normalize_path(path):
    allowed = string.ascii_letters + string.digits + '._'
    return ''.join([char if char in allowed else '_' for char in path])


def sync(dry_run, target, allow_formats, album_per_dir, number_dirs,
         number_files, playlist):
    allow_formats = allow_formats or ['all']

    operations = []
    for item_number, item in enumerate(playlist):
        if 'location' in item:
            path = calliope.uri_to_path(item['location'])
            if number_files:
                filename = ensure_number(os.path.basename(path), item_number + 1)
            else:
                filename = None  # use existing
            operations.append(
                sync_track(item['location'], target, allow_formats,
                            target_filename=filename))
        elif 'tracks' in item:
            for track_number, track_item in enumerate(item['tracks']):
                if 'location' in track_item:
                    path = calliope.uri_to_path(track_item['location'])
                    if number_files:
                        filename = ensure_number(
                            os.path.basename(path),
                            track_number + 1)
                    else:
                        filename = None  # use existing

                    if album_per_dir:
                        album_name = item.get('album') or 'No album'
                        if number_dirs:
                            dirname = make_dirname('%03i' % (item_number + 1),
                                                    item['artist'],
                                                    album_name)
                        else:
                            dirname = make_dirname(item['artist'],
                                                    album_name)
                    else:
                        dirname = None  # use existing

                    if filename:
                        target_filename = normalize_path(filename)
                    else:
                        target_filename = None

                    if dirname:
                        target_dirname = normalize_path(dirname)
                    else:
                        target_dirname = None

                    operations.append(
                        sync_track(track_item['location'], target,
                                    allow_formats,
                                    target_filename=target_filename,
                                    target_dirname=target_dirname))

    if dry_run:
        for operation in operations:
            print(operation)
    else:
        for operation in operations:
            log.debug(str(operation))
            operation.run()
