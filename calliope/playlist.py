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


class PlaylistKind(enum.Enum):
    COLLECTION = 0
    PLAYLIST = 1


def process_playlist(yaml_parsed):
    if 'collection' in yaml_parsed:
        kind = PlaylistKind.COLLECTION
        items = yaml_parsed['collection'] or []
    elif 'playlist' in yaml_parsed:
        kind = PlaylistKind.PLAYLIST
        items = yaml_parsed['playlist'] or []
    elif 'list' in yaml_parsed:
        kind = PlaylistKind.PLAYLIST
        items = yaml_parsed['list'] or []
    else:
        raise RuntimeError ("Expected 'playlist' or 'collection' entry")

    return kind, items


class Playlist():
    '''A playlist is a set of songs.

    A 'collection' is also considered to be a playlist, but one where order
    isn't important.

    '''
    def __init__(self, yaml_parsed=None):
        if not yaml_parsed:
            self.kind = PlaylistKind.PLAYLIST
            self.items = []
        else:
            self.kind, self.items = process_playlist(yaml_parsed)

        for i, item in enumerate(self.items):
            if isinstance(item, str):
                self.items[i] = {'track': item}

    def __iter__(self):
        return iter(self.items)

    def append(self, playlist):
        self.items += playlist.items


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

    Returns an iterator of calliope.playlist.Item objects.

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
