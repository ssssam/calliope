# Calliope Playlist Viewer
#
# Copyright 2018 Sam Thursfield <sam@afuera.me.uk>
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


import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gio, GLib, GObject, Gtk


class PlaylistItem(GObject.Object):
    '''GObject wrapper for calliope.playlist.Item.

    This is needed because a GListModel can only contain GObject subclasses.

    '''
    def __init__(self, item):
        super(PlaylistItem, self).__init__()
        self.item = item

    def __getitem__(self, key):
        return self.item[key]

    def title(self):
        artist = self.item.get('artist')
        album = self.item.get('album')
        track = self.item.get('track')

        parts = []

        if artist:
            parts.append(artist)
        if album:
            parts.append(album)
        if track:
            parts.append(track)

        if len(parts) == 0:
            return 'Unknown item'
        else:
            return ' - '.join(parts)


class PlaylistModel(GObject.Object, Gio.ListModel):
    def __init__(self, items):
        super(PlaylistModel, self).__init__()
        self.items = [PlaylistItem(i) for i in items]

    def do_get_n_items(self):
        return len(self.items)

    def do_get_item(self, position):
        item = self.items[position]
        return item
