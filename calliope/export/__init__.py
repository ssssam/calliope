# Calliope
# Copyright (C) 2016,2018  Sam Thursfield <sam@afuera.me.uk>
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


def convert_to_cue(playlist):
    output_text = ['FILE "none" WAVE']
    for i, item in enumerate(playlist):
        output_text.append("  TRACK %02i AUDIO" % (i + 1))
        if 'track' in item:
            output_text.append("    TITLE \"%s\"" % item['track'])
        if 'artist' in item:
            output_text.append("    PERFORMER \"%s\"" % item['artist'])
        if 'start-time' in item:
            timestamp = item['start-time']
        else:
            if i == 0:
                timestamp = 0
            else:
                raise RuntimeError("The 'start-time' field must be set for all entries "
                                   "in order to create a CUE sheet")
        output_text.append("  INDEX 01 %02i:%02i:00" % (int(timestamp / 60), int(timestamp % 60)))
    return '\n'.join(output_text)


def convert_to_m3u(playlist):
    output_text = []
    for i, item in enumerate(playlist):
        if 'location' in item:
            output_text.append(item['location'])
        else:
            raise RuntimeError("The 'location' field must be set for all entries "
                                "in order to create an M3U playlist")
    return '\n'.join(output_text)
