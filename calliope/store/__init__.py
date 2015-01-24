# Calliope -- storage module
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


import yoyo

import logging
import os
import re
import sqlite3


log = logging.getLogger(__name__)


_escape_re = re.compile('[^a-zA-Z0-9]')
def escape_for_sql_identifier(name):
    return re.sub(_escape_re, '_', name)


class Store:
    def __init__(self, file_path):
        self.db = sqlite3.connect(file_path)
        self.apply_migrations('store', self.migrations_dir())

    def migrations_dir(self):
        return os.path.join(os.path.dirname(__file__), 'migrations')

    def apply_migrations(self, namespace, migrations_path):
        migration_table = 'migration_%s' % escape_for_sql_identifier(namespace)
        migrations = yoyo.read_migrations(self.db, sqlite3.paramstyle,
                                          migrations_path,
                                          migration_table=migration_table)
        to_apply = migrations.to_apply()
        log.info('Found %i migrations for %s, applying %i', len(migrations),
                 namespace, len(to_apply))
        to_apply.apply()
        self.db.commit()
