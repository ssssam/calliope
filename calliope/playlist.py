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


import yaml

import enum
import sys


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

    def dump(self, stream):
        kind_name = 'collection' if self.kind == PlaylistKind.COLLECTION else 'playlist'
        document = { kind_name: self.items }
        yaml.safe_dump(document, sys.stdout, default_flow_style=False)

    def tracks(self):
        for item in self.items:
            if 'track' in item:
                yield item
            elif 'album' in item and 'tracks' in item:
                for track in item['tracks']:
                    track_merged = copy.copy(track)
                    track_merged['album'] = item['album']
                    if item.get('artist') and 'artist' not in track_merged:
                        track_merged['artist'] = item['artist']
                    yield track_merged


