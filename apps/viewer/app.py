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

from gettext import gettext as _

import copy
import logging
import time

import calliope.apps.viewer.mainwindow
import calliope.apps.viewer.playlistmodel


class Application(Gtk.Application):
    def __init__(self, playlist_stream=None, app_id_suffix=None):
        application_id = 'uk.me.afuera.Calliope.Apps.Viewer'

        # This is allowed for testing purposes only.
        if app_id_suffix:
            application_id += app_id_suffix

        Gtk.Application.__init__(self, application_id=application_id,
                                 flags=Gio.ApplicationFlags.FLAGS_NONE)

        #self.settings = Gio.Settings.new('uk.me.afuera.Tagcloud')

        self._window = None

        self.playlist = calliope.apps.viewer.playlistmodel.PlaylistModel(
            list(calliope.playlist.read(playlist_stream)))

    def do_activate(self):
        if not self._window:
            self._window = calliope.apps.viewer.mainwindow.MainWindow(self)

        self._window.set_playlist(self.playlist)
        self._window.present()
