# Calliope
# Copyright (C) 2017  Sam Thursfield <sam@afuera.me.uk>
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


import configparser
import os
import xdg.BaseDirectory


class Configuration(configparser.ConfigParser):
    def __init__(self):
        super(Configuration, self).__init__()
        self.read(
            os.path.join(config_dir, 'calliope.conf')
            for config_dir in xdg.BaseDirectory.xdg_config_dirs)


__configuration = None

def get(section, option):
    global __configuration
    if __configuration == None:
        __configuration = Configuration()
    if __configuration.has_section(section):
        return __configuration.get(section, option)
    else:
        return None
