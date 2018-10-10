# Calliope Viewer App
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


from gi.repository import Gdk, Gio, GLib, GObject, Gtk

import logging
from gettext import gettext as _

import calliope.apps.viewer.playlistbox


GDK_EVENT_PROPAGATE = False
GDK_EVENT_STOP = True


class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        Gtk.ApplicationWindow.__init__(self,
                                       application=app,
                                       title=_("Calliope Playlist Viewer"))

        builder = Gtk.Builder()
        builder.add_from_resource('/uk/me/afuera/Calliope/Apps/Viewer/mainwindow.ui')

        self.playlist_model = None
        self.playlist_box = calliope.apps.viewer.playlistbox.PlaylistBox()

        playlist_box_container = builder.get_object('playlist-container')
        playlist_box_container.add(self.playlist_box)

        self.child_widgets_from_builder(builder, 'main-window')

    def child_widgets_from_builder(self, builder, object_name):
        '''Set window contents from the given Gtk Builder instance.

        This is a workaround for the fact that we cannot create a working
        GtkApplicationWindow instance directly from the .ui file.

        '''
        window = builder.get_object(object_name)
        headerbar = window.get_titlebar()
        window.remove(headerbar)
        self.set_titlebar(headerbar)

        child = window.get_child()
        window.remove(child)
        self.add(child)
        self.show_all()

    def set_playlist(self, model):
        self.playlist_model = model
        self.playlist_box.set_model(model)
