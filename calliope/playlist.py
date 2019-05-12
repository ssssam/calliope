# Calliope
# Copyright (C) 2016, 2018  Sam Thursfield <sam@afuera.me.uk>
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


import enum
import json
import sys


class PlaylistError(RuntimeError):
    pass


class Item(dict):
    '''Represents a single item in a Calliope playlist.'''
    def __init__(self, data):
        # FIXME: let's not be this dumb.
        self.update(data)

    def id(self):
        if 'id' in self:
            return self['id']
        else:
            return '%s.%s' % (self.get('artist').lower(), self.get('track').lower())

    def tracks(self):
        '''Return all the tracks for this playlist item.

        In many cases one item corresponds to one track. However, this isn't
        guaranteed. For example a playlist may be a list of albums, each of
        which contains multiple tracks.

        '''
        if 'track' in self:
            return self
        elif 'album' in self and 'tracks' in self:
            for track in self['tracks']:
                track_merged = copy.copy(track)
                track_merged['album'] = self['album']
                if self.get('artist') and 'artist' not in track_merged:
                    track_merged['artist'] = self['artist']
                yield track_merged


# Adapted from https://stackoverflow.com/questions/6886283/how-i-can-i-lazily-read-multiple-json-values-from-a-file-stream-in-python/7795029
def _iterload(f, cls=json.JSONDecoder, **kwargs):
    decoder = cls(**kwargs)

    while True:
        line = f.readline()

        if len(line) == 0:
            break

        idx = json.decoder.WHITESPACE.match(line, 0).end()
        while idx < len(line):
            obj, end = decoder.raw_decode(line, idx)
            yield obj
            idx = json.decoder.WHITESPACE.match(line, end).end()


def read(stream):
    '''Parses a playlist from the given stream.

    Returns an generator that produces calliope.playlist.Item objects.

    The generator will read from the file on demand, so you must be careful not
    to do this:

        with open('playlist.cpe', 'r') as f:
            playlist = calliope.playlist.read(f)

        for item in playlist:
            # You will see 'ValueError: I/O operation on closed file.'.
            ...

    If you want to read the playlist in one operation, convert it to a list:

        with open('playlist.cpe', 'r') as f:
            playlist = list(calliope.playlist.read(f))

    '''
    for json_object in _iterload(stream):
        if isinstance(json_object, dict):
            yield Item(json_object)
        else:
            raise PlaylistError("Expected JSON object, got {}".format(type(json_object).__name__))


def write(items, stream):
    '''Write a playlist to the given stream.'''
    for item in items:
        json.dump(item, stream)
        stream.write('\n')
