# Calliope -- database migrations for main store
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


from yoyo import step, transaction


transaction(
step(
    'CREATE TABLE items ('
    '   id INTEGER UNIQUE PRIMARY KEY, '
    '   uri VARCHAR UNIQUE NOT NULL, '
    '   musicbrainz_id VARCHAR '
    ')',
    'DROP TABLE items'
),
step(
    'CREATE TABLE plays ('
    '   id INTEGER UNIQUE PRIMARY KEY,'
    '   date DATETIME NOT NULL,'
    '   item_id INTEGER NOT NULL,'
    '   FOREIGN KEY (item_id) REFERENCES items(id)'
    ')',
    'DROP TABLE plays'
)
)
