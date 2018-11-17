# Calliope
# Copyright (C) 2018  Sam Thursfield <sam@afuera.me.uk>
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


import xdg.BaseDirectory

import contextlib
import dbm.gnu
import errno
import json
import io
import logging
import os
import time

log = logging.getLogger(__name__)

'''cache: Simple key-value store for use by Calliope tools.

Many Calliope tools contact online services. We should always cache the
responses we get to avoid repeating the same request. This module provides a
simple key/value store interface that should be used for caching.

Use the `open()` module method to access a cache.

Multiple processes can read and write to a cache concurrently and can share data
appropriately.

'''

class Cache():
    '''Abstract base class that defines the Cache interface.

    Do not use this class directly. Call the `open()` module method instead.

    '''
    def __init__(self, namespace, cachedir=None):
        raise NotImplementedError("Use the cache.open() function to open a cache")

    def lookup(self, key):
        '''Lookup 'key' in the cache.

        Returns a tuple of (found, value).

        '''
        raise NotImplementedError()

    def store(self, key, value):
        '''Store 'value' in the cache under the given key.

        The contents of 'value' must be representable as JSON data.

        '''
        raise NotImplementedError()


class GdbmCache:
    '''Cache implementation which uses the GNU DBM library.'''

    # GDBM does not support concurrent writers & readers. To work around this
    # we re-open the database on every read and write. This probably has a
    # performance penalty.

    def __init__(self, namespace, cachedir=None):
        if cachedir is None:
            cachedir = xdg.BaseDirectory.save_cache_path('calliope')

        self._path = os.path.join(cachedir, namespace) + '.gdbm'

    def lookup(self, key):
        '''Lookup 'key' in the cache.

        Returns a tuple of (found, value).

        '''
        if not os.path.exists(self._path):
            return False, None
        with dbm.gnu.open(self._path, 'r') as db:
            if key in db:
                return True, json.loads(db[key])
            else:
                return False, None

    @contextlib.contextmanager
    def _open_for_writing(self):
        # Open the database for writing. If it is currently locked for reading,
        # wait a bit and try again.

        MAX_RETRIES = 3
        for attempt in range(1,MAX_RETRIES+1):
            try:
                db = dbm.gnu.open(self._path, 'cf')
                yield db
                db.close()

                break   # Exit the retry loop -- we succeeded.
            except dbm.gnu.error as e:
                if e.errno == errno.EAGAIN:   # error 11 -- database is locked
                    delay = 10**attempt
                    log.debug("Database locked. Retrying in {} msec ({}/{}).".
                              format(delay, attempt, MAX_RETRIES))
                    time.sleep(delay * 0.001)
                else:
                    raise
        else:
            raise RuntimeError(
                "Cache is locked -- unable to write despite {} attempts.".
                format(attempt))

    def store(self, key, value):
        with self._open_for_writing() as db:
            db[key] = json.dumps(value)


def open(namespace, cachedir=None):
    '''Open a cache using the best available cache implementation.

    The 'namespace' parameter should usually correspond with the name of tool
    or module using the cache.

    The 'cachedir' parameter is mainly for use during automated tests.

    '''
    return GdbmCache(namespace, cachedir=cachedir)
