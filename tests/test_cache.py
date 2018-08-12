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


import calliope


def test_dict(tmpdir):
    '''Store and retrieve a dictionary value.'''
    cache = calliope.cache.Cache('test', cachedir=tmpdir)

    key = 'foo'
    value = {'a': 5, 'b': 4}

    found, returned_value = cache.lookup(key)
    assert found == False
    assert returned_value == None

    cache.store(key, value)

    found, returned_value = cache.lookup(key)

    assert found == True
    assert returned_value == value


def test_null_value(tmpdir):
    '''Store and retrieve a null value.'''
    cache = calliope.cache.Cache('test', cachedir=tmpdir)

    key = 'foo'
    value = None

    found, returned_value = cache.lookup(key)
    assert found == False
    assert returned_value == None

    cache.store(key, value)

    found, returned_value = cache.lookup(key)

    assert found == True
    assert returned_value == value