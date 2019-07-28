# Calliope
# Copyright (C) 2019  Sam Thursfield <sam@afuera.me.uk>
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


import io
import json

import calliope


# Example xspf taken from http://www.xspf.org/quickstart/
example_1 = """<?xml version="1.0" encoding="UTF-8"?>
<playlist version="1" xmlns="http://xspf.org/ns/0/">
    <title>80s Music</title>
    <creator>Jane Doe</creator>
    <info>http://example.com/~jane</info>

    <trackList>
        <track>
            <location>http://example.com/song_1.mp3</location>
            <creator>Led Zeppelin</creator>
            <album>Houses of the Holy</album>
            <title>No Quarter</title>
            <annotation>I love this song</annotation>
            <duration>271066</duration>
            <image>http://images.amazon.com/images/P/B000002J0B.01.MZZZZZZZ.jpg</image>
            <info>http://example.com</info>
        </track>
    </trackList>
</playlist>
"""

# Example jspf taken from http://www.xspf.org/jspf/
example_2 = """{
  "playlist" : {
    "title"         : "Two Songs From Thriller",
    "creator"       : "MJ Fan",
    "track"         : [
      {
        "location"      : ["http://example.com/billiejean.mp3"], 
        "title"         : "Billie Jean",
        "creator"       : "Michael Jackson",
        "album"         : "Thriller"
      }, 
      {
      "location"      : ["http://example.com/thegirlismine.mp3"], 
      "title"         : "The Girl Is Mine",
      "creator"       : "Michael Jackson",
      "album"         : "Thriller"
      }
    ]
  }
}
"""


def test_xspf_basic(cli):
    result = cli.run(['--debug', 'import', '-'], input=example_1)

    assert result.exit_code == 0

    items = list(calliope.playlist.read(io.BytesIO(result.output.encode('utf-8'))))

    assert items == [
        {"location": "http://example.com/song_1.mp3",
         "track": "No Quarter",
         "artist": "Led Zeppelin",
         "comment": "I love this song",
         "xspf.info": "http://example.com",
         "image": "http://images.amazon.com/images/P/B000002J0B.01.MZZZZZZZ.jpg",
         "album": "Houses of the Holy",
         "duration": 271.066,
         "playlist.title": "80s Music",
         "playlist.creator": "Jane Doe",
         "playlist.info": "http://example.com/~jane"
        }
    ]


def test_jspf_basic(cli):
    result = cli.run(['--debug', 'import', '-'], input=example_2)

    assert result.exit_code == 0

    items = list(calliope.playlist.read(io.BytesIO(result.output.encode('utf-8'))))

    assert items == [
        {
            "location": "http://example.com/billiejean.mp3",
            "track": "Billie Jean",
            "artist": "Michael Jackson",
            "album": "Thriller",
            "playlist.title": "Two Songs From Thriller",
            "playlist.creator": "MJ Fan"
        },
        {
            "location": "http://example.com/thegirlismine.mp3",
            "track": "The Girl Is Mine",
            "artist": "Michael Jackson",
            "album": "Thriller"
        }
    ]
