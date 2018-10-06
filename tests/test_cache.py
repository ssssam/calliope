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


import pytest

import calliope

import threading


KINDS = [calliope.cache.JsonCache, calliope.cache.GdbmCache]


@pytest.fixture
def cache(tmpdir, kind):
    return kind(namespace='test', cachedir=tmpdir)


@pytest.mark.parametrize('kind', KINDS)
def test_dict(cache):
    '''Store and retrieve a dictionary value.'''
    key = 'foo'
    value = {'a': 5, 'b': 4}

    found, returned_value = cache.lookup(key)
    assert found == False
    assert returned_value == None

    cache.store(key, value)

    found, returned_value = cache.lookup(key)

    assert found == True
    assert returned_value == value


@pytest.mark.parametrize('kind', KINDS)
def test_null_value(cache):
    '''Store and retrieve a null value.'''
    key = 'foo'
    value = None

    found, returned_value = cache.lookup(key)
    assert found == False
    assert returned_value == None

    cache.store(key, value)

    found, returned_value = cache.lookup(key)

    assert found == True
    assert returned_value == value


class Counter():
    '''Helper class used by benchmark tests.'''
    def __init__(self, limit=None):
        self.value = 0
        self.limit = limit

    def next(self):
        self.value += 1
        if self.limit is not None and self.value >= self.limit:
            self.value = 0

    def get(self):
        return self.value


@pytest.mark.parametrize('kind', KINDS)
@pytest.mark.benchmark(min_rounds=100)
def test_read_speed(cache, benchmark):
    # First, write 1000 values to the cache.
    for i in range(0, 1000):
        key = 'test:%i' % i
        test_data = 100*chr((i%26)+65)
        cache.store(key, test_data)

    def read_value(cache, counter):
        '''Test function: Read 1 value from the cache.'''
        counter.next()
        key = 'test:%i' % counter.get()
        found, value = cache.lookup(key)
        assert found
        assert len(value) == 100

    counter = Counter(limit=1000)
    benchmark(read_value, cache, counter)


@pytest.mark.parametrize('kind', KINDS)
@pytest.mark.benchmark(min_rounds=100)
def test_write_speed(cache, benchmark):
    def store_new_value(cache, counter):
        '''Test function: Write 1 value to the cache.'''
        counter.next()
        key = 'test:%i' % counter.get()
        test_data = 100*chr((counter.get()%26)+65)
        cache.store(key, test_data)

    counter = Counter()
    benchmark(store_new_value, cache, counter)


@pytest.mark.parametrize('kind', KINDS)
def test_concurrent_writes(kind, tmpdir):
    '''Test that two threads can write to the same cache file at once.'''
    class Thread1(threading.Thread):
        def run(self):
            cache = kind('benchmark', cachedir=tmpdir)
            for i in range(0, 1000):
                key = 'test:%i' % i
                test_data = 100*chr((i%26)+65)
                cache.store(key, test_data)

    class Thread2(threading.Thread):
        def run(self):
            cache = kind('benchmark', cachedir=tmpdir)
            for i in range(500, 1500):
                key = 'test:%i' % i
                test_data = 100*chr((i%26)+65)
                cache.store(key, test_data)

    t1 = Thread1()
    t2 = Thread2()
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    cache = kind('benchmark', cachedir=tmpdir)
    for i in range(0, 1500):
        found, value = cache.lookup('test:%i' % i)
        assert found
        assert len(value) == 100
