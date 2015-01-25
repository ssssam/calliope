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
import datetime
import logging
import sys

import miners
import store
import views.bucket


# FIXME: make this configurable
STORE_PATH = 'calliope.db'


class AppException:
    pass


def display_timestamp(timestamp):
    time_datetime = datetime.datetime.fromtimestamp(timestamp)
    return time_datetime.strftime('%s')

def display_uri(uri):
    # FIXME: this should be pluggable, right now it's a bit of a hack
    if uri.startswith('lastfm://'):
        parts = uri.strip('lastfm://').split('/')
        return 'http://last.fm/music/%s/_/%s' % (parts[0], '/'.join(parts[1:]))


class CalliopeCommandLineInterface:
    def create_argparse(self):
        parser = argparse.ArgumentParser(
            description='Calliope commandline interface')

        subparsers = parser.add_subparsers()
        parser_sync = subparsers.add_parser('sync')
        parser_sync.set_defaults(func=self.cmd_sync)

        parser_view_bucket = subparsers.add_parser('view-bucket')
        bucket_subparsers = parser_view_bucket.add_subparsers()

        bucket_neglected = bucket_subparsers.add_parser('neglected')
        bucket_neglected.set_defaults(func=self.cmd_view_bucket_neglected)

        #parser_view_bucket.set_defaults(func=self.cmd_view_bucket)

        return parser

    def run(self, args):
        logging.basicConfig(level=logging.DEBUG)

        parser = self.create_argparse()
        args = parser.parse_args(args)

        if 'func' in args:
            args.func(args)
        else:
            parser.print_help()

    def cmd_sync(self, args):
        print('Loading Calliope store and miners...')
        db = store.Store(STORE_PATH)
        loaded_miners = miners.load_all(db)

        for m in loaded_miners:
            print('Syncing %s' % m)
            m.sync()

    def cmd_view_bucket(self, args):
        db = store.Store(STORE_PATH)
        view = views.bucket.BucketView(db)

        if len(args) == 0:
            # All items in the bucket
            for item in view:
                print(item)

    def cmd_view_bucket_neglected(self, args):
        db = store.Store(STORE_PATH)
        view = views.bucket.BucketView(db)

        for uri, timestamp in view.neglected():
            print('%s\t%s' % (display_timestamp(timestamp), display_uri(uri)))


CalliopeCommandLineInterface().run(sys.argv[1:])
