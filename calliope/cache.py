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


import contextlib
import json
import logging
import os
import tempfile
import time
import xdg.BaseDirectory

log = logging.getLogger(__name__)


# Adapted from BuildStream:
# https://gitlab.com/BuildStream/buildstream/blob/master/buildstream/utils.py
@contextlib.contextmanager
def save_file_atomic(filename, mode='w', *, buffering=-1, encoding=None,
                     errors=None, newline=None, closefd=True, opener=None):
    '''Save a file with a temporary name and rename it into place when ready.

    This is a context manager which is meant for saving data to files.
    The data is written to a temporary file, which gets renamed to the target
    name when the context is closed. This avoids readers of the file from
    getting an incomplete file.

    **Example:**

    .. code:: python

      with save_file_atomic('/path/to/foo', 'w') as f:
          f.write(stuff)

    The file will be called something like ``tmpCAFEBEEF`` until the
    context block ends, at which point it gets renamed to ``foo``. The
    temporary file will be created in the same directory as the output file.
    The ``filename`` parameter must be an absolute path.

    If an exception occurs or the process is terminated, the temporary file will
    be deleted.
    '''
    # This feature has been proposed for upstream Python in the past, e.g.:
    # https://bugs.python.org/issue8604

    assert os.path.isabs(filename), "The utils.save_file_atomic() parameter ``filename`` must be an absolute path"
    dirname = os.path.dirname(filename)
    fd, tempname = tempfile.mkstemp(dir=dirname)
    os.close(fd)

    f = open(tempname, mode=mode, buffering=buffering, encoding=encoding,
             errors=errors, newline=newline, closefd=closefd, opener=opener)

    def cleanup_tempfile():
        f.close()
        try:
            os.remove(tempname)
        except FileNotFoundError:
            pass
        except OSError as e:
            raise UtilError("Failed to cleanup temporary file {}: {}".format(tempname, e)) from e

    try:
        f.real_filename = filename
        yield f
        f.close()
        # This operation is atomic, at least on platforms we care about:
        # https://bugs.python.org/issue8828
        os.replace(tempname, filename)
    except Exception:
        cleanup_tempfile()
        raise


class Cache:
    '''Simple key-value store for use by Calliope tools.

    Many Calliope tools contact online services. We should always cache the
    responses we get to avoid repeating the same request. This class provides a
    simple key/value store interface that should be used for caching.

    Currently the implementation is very simple and dumb. All data is stored on
    disk in a JSON file, which is read each time we look up a value and written
    every time we save a value. A more scalable solution will no doubt be needed
    in future.

    '''
    def __init__(self, namespace, cachedir=None):
        if cachedir is None:
            cachedir = xdg.BaseDirectory.save_cache_path('calliope')

        self._path = os.path.join(cachedir, namespace)

        self._data = {}
        self._mtime = None

    def _load(self):
        try:
            with open(self._path) as f:
                self._data = json.load(f)
            self._mtime = time.time()
        except FileNotFoundError as e:
            pass

    def _save(self):
        with save_file_atomic(self._path) as f:
            json.dump(self._data, f)
        self._mtime = time.time()

    def _check_reload(self):
        if self._mtime is None:
            log.debug("Loading cache for the first time")
            self._load()
        else:
            mtime = os.stat(self._path).st_mtime
            if self._mtime < mtime:
                log.debug("Cache has been updated (new mtime is {})".format(mtime))
                self._load()

    def lookup(self, key):
        '''Lookup 'key' in the cache.

        Returns a tuple of (found, value).

        '''
        self._check_reload()
        if key in self._data:
            return True, self._data[key]
        else:
            return False, None

    def store(self, key, value):
        self._data[key] = value
        self._save()
