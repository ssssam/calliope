# Calliope -- last.fm miner
# Copyright (C) 2015  Sam Thursfield <sam@afuera.me.uk>
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


import os


class LastfmMiner:
    def __init__(self):
        pass

    def migrations_dir(self):
        return os.path.join(os.path.dirname(__file__), 'migrations', 'lastfm')


def load(store):
    miner = LastfmMiner()
    store.apply_migrations('miner.lastfm', miner.migrations_dir())
    return miner
