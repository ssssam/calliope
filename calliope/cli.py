#!/usr/bin/env python3
# Calliope
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


import argparse
import logging
import sys

import miners
import store


# FIXME: make this configurable
STORE_PATH = 'calliope.db'


class CalliopeCommandLineInterface:
    def load(self):
        self.store = store.Store(STORE_PATH)
        self.miners = miners.load_all(self.store)

    def run(self, args):
        logging.basicConfig(level=logging.DEBUG)
        print('Loading Calliope store and miners...')
        self.load()
        print('State of each miner:')
        for m in self.miners:
            print(m.status())


CalliopeCommandLineInterface().run(sys.argv[1:])
