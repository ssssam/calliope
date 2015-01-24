# Calliope -- database migrations for last.fm miner
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


from yoyo import step


step(
    'CREATE TABLE imports_lastfm ('
    '   id INTEGER UNIQUE PRIMARY KEY, '
    '   item_id INTEGER NOT NULL, '
    '   play_id INTEGER NOT NULL, '
    '   date DATETIME NOT NULL, '
    '   trackname VARCHAR, '
    '   artistname VARCHAR, '
    '   albumname VARCHAR, '
    '   trackmbid VARCHAR, '
    '   artistmbid VARCHAR, '
    '   albummbid VARCHAR, '
    '   FOREIGN KEY (item_id) REFERENCES items(id), '
    '   FOREIGN KEY (play_id) REFERENCES plays(id)'
    ')',
    'DROP TABLE imports_lastfm'
)
