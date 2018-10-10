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


from gi.repository import Gtk


class PlaylistBox(Gtk.ListBox):
    def _create_item_cb(self, item, user_data):
        builder = Gtk.Builder.new_from_resource('/uk/me/afuera/Calliope/Apps/Viewer/playlistitem.ui')
        widget = builder.get_object('playlist-item')
        widget.item = item

        label = builder.get_object('text')
        label.set_text(item.title())

        widget.show_all()
        return widget

    def set_model(self, playlist):
        self.model = playlist
        self.bind_model(playlist, self._create_item_cb, None)
