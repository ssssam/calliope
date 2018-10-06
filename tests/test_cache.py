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
