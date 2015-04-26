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


import store


class BucketView:
    '''The bucket view

    The bucket contains every track you have listened to.

    '''
    def __init__(self, store):
        self.store = store

    def __iter__(self):
        '''Iterate through the URI of every item in the bucket.

        This function is for testing only.

        '''
        cursor = self.store.cursor()
        result = cursor.execute(
            'SELECT DISTINCT items.uri '
            'FROM plays INNER JOIN items '
            'WHERE plays.item_id = items.id')
        for row in result:
            yield row[0]

    def neglected(self):
        '''What hasn't been listened to for the longest time?'''

        cursor = self.store.cursor()
        result = cursor.execute(
            'SELECT items.uri, datetime '
            'FROM items, ( '
            '   SELECT plays.item_id, MAX(plays.datetime) AS datetime'
            '   FROM plays '
            '   GROUP BY plays.item_id'
            ') '
            'WHERE items.id = item_id '
            'ORDER BY datetime'
        )
        for row in result:
            yield row[0], row[1]
