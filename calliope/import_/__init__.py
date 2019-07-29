# Calliope
# Copyright (C) 2016  Sam Thursfield <sam@afuera.me.uk>
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

'''calliope-import

Convert playlists and collections from different serialization formats.

'''

import click
import yaml

import configparser
import enum
import logging
import sys
import xml.etree.ElementTree

import calliope

log = logging.getLogger(__name__)


class PlaylistFormat(enum.Enum):
    PLS = 1

    # http://www.xspf.org/ and http://www.xspf.org/jspf/
    #
    # Note that we allow YAML as well as JSON for JSPF format playlists.
    XSPF = 2
    JSPF = 3


class PlaylistReadError(Exception):
    pass


def guess_format(text):
    '''Guess the format of the input playlist.

    This is a simple function which tries different parsers in succession
    until one succeeds. It's not the most efficient way to load a playlist.

    '''
    try:
        log.debug("guess_format: Checking INI-style format (pls)")
        parser = configparser.ConfigParser()
        parser.read_string(text)
        if parser.has_section('playlist'):
            return PlaylistFormat.PLS
    except (UnicodeDecodeError, configparser.Error) as e:
        log.debug("guess_format: Got exception: %s", e)
        pass

    try:
        log.debug("guess_format: Checking XML format (xspf)")
        tree = xml.etree.ElementTree.fromstring(text)
        if tree.tag == '{http://xspf.org/ns/0/}playlist':
            return PlaylistFormat.XSPF
    except xml.etree.ElementTree.ParseError as e:
        log.debug("guess_format: Got exception: %s", e)
        pass

    try:
        log.debug("guess_format: Checking YAML / JSON format (jspf)")
        # JSON is a subset of YAML, so we're just gonna try YAML here.
        doc = yaml.safe_load(text)
        if not isinstance(doc, dict) or len(doc) == 0:
            log.debug("guess_format: JSON/YAML parsing succeeded but the document is empty or not a dict.")
        elif 'playlist' in doc:
            return PlaylistFormat.JSPF
    except yaml.YAMLError as e:
        log.debug("guess_format: Got exception: %s", e)
        pass

    return None


def parse_pls(text):
    parser = configparser.ConfigParser(interpolation=None)
    parser.read_string(text)
    number_of_entries = parser.getint('playlist', 'NumberOfEntries')

    entries = []
    for i in range(1, number_of_entries+1):
        entry = {
            'location': parser.get('playlist', 'File%i' % i),
            'track': parser.get('playlist', 'Title%i' % i)
        }
        entries.append(calliope.playlist.Item(entry))
    return entries


def parse_xspf(text):
    tree = xml.etree.ElementTree.fromstring(text)

    if tree.tag != '{http://xspf.org/ns/0/}playlist':
        raise PlaylistReadError("Invalid XSPF: No top-level <playlist> tag.")

    tracklist = tree.find('{http://xspf.org/ns/0/}trackList')
    if tracklist is None:
        raise PlaylistReadError("Invalid XSPF: No <trackList> section.")

    def xspf_tag_to_calliope_property(element, entry, tag, property):
        first_child_element = element.find(tag)
        if first_child_element != None:
            entry[property] = first_child_element.text

    entries = []
    for track in tracklist:
        entry = {}

        # XSPF tracks can have multiple <location> and <identifier> tags.
        # We currently just use the first of each.
        xspf_tag_to_calliope_property(track, entry, '{http://xspf.org/ns/0/}location', 'location')
        xspf_tag_to_calliope_property(track, entry, '{http://xspf.org/ns/0/}identifier', 'id')

        # These tags shouldn't appear more than once. All are optional though.
        xspf_tag_to_calliope_property(track, entry, '{http://xspf.org/ns/0/}title', 'track')
        xspf_tag_to_calliope_property(track, entry, '{http://xspf.org/ns/0/}creator', 'artist')
        xspf_tag_to_calliope_property(track, entry, '{http://xspf.org/ns/0/}annotation', 'comment')
        xspf_tag_to_calliope_property(track, entry, '{http://xspf.org/ns/0/}info', 'xspf.info')
        xspf_tag_to_calliope_property(track, entry, '{http://xspf.org/ns/0/}image', 'image')
        xspf_tag_to_calliope_property(track, entry, '{http://xspf.org/ns/0/}album', 'album')
        xspf_tag_to_calliope_property(track, entry, '{http://xspf.org/ns/0/}trackNum', 'album.track-number')
        xspf_tag_to_calliope_property(track, entry, '{http://xspf.org/ns/0/}duration', 'duration')

        if 'duration' in entry:
            # Convert from milliseconds to seconds.
            entry['duration'] = int(entry['duration']) / 1000.0

        # We currently ignore the <link>, <meta> and <extension> tags.

        if len(entry) == 0:
            log.warn("Empty <track> entry found.")

        entries.append(entry)

    if len(entries) > 0:
        # If the playlist has metadata tags, we store them on the first entry
        # that we return.
        metadata_entry = entries[0]
        xspf_tag_to_calliope_property(tree, metadata_entry, '{http://xspf.org/ns/0/}title', 'playlist.title')
        xspf_tag_to_calliope_property(tree, metadata_entry, '{http://xspf.org/ns/0/}creator', 'playlist.creator')
        xspf_tag_to_calliope_property(tree, metadata_entry, '{http://xspf.org/ns/0/}annotation', 'playlist.annotation')
        xspf_tag_to_calliope_property(tree, metadata_entry, '{http://xspf.org/ns/0/}info', 'playlist.info')
        xspf_tag_to_calliope_property(tree, metadata_entry, '{http://xspf.org/ns/0/}location', 'playlist.location')
        xspf_tag_to_calliope_property(tree, metadata_entry, '{http://xspf.org/ns/0/}identifier', 'playlist.identifier')
        xspf_tag_to_calliope_property(tree, metadata_entry, '{http://xspf.org/ns/0/}image', 'playlist.image')
        xspf_tag_to_calliope_property(tree, metadata_entry, '{http://xspf.org/ns/0/}date', 'playlist.date')
        xspf_tag_to_calliope_property(tree, metadata_entry, '{http://xspf.org/ns/0/}license', 'playlist.license')

        # We currently ignore the <attribution> and <link> tags.

    return entries


def parse_jspf(text):
    doc = yaml.safe_load(text)

    if 'playlist' not in doc:
        raise PlaylistReadError("Invalid XSPF: No top-level 'playlist' item.")
    playlist = doc['playlist']

    if 'track' not in playlist:
        raise PlaylistReadError("Invalid XSPF: No 'track' list.")
    tracklist = playlist['track']

    def jspf_to_calliope(jspf_entry, calliope_entry, jspf_property, calliope_property):
        if jspf_property in jspf_entry:
            calliope_entry[calliope_property] = jspf_entry[jspf_property]

    entries = []
    for track in tracklist:
        entry = {}

        jspf_to_calliope(track, entry, 'location', 'location')
        jspf_to_calliope(track, entry, 'identifier', 'id')

        # XSPF tracks can have multiple <location> and <identifier> tags.
        # We currently just use the first of each.
        if 'location' in entry and isinstance(entry['location'], list):
            entry['location'] = entry['location'][0]
        if 'id' in entry and isinstance(entry['id'], list):
            entry['id'] = entry['id'][0]

        # These tags shouldn't appear more than once. All are optional though.
        jspf_to_calliope(track, entry, 'title', 'track')
        jspf_to_calliope(track, entry, 'creator', 'artist')
        jspf_to_calliope(track, entry, 'annotation', 'comment')
        jspf_to_calliope(track, entry, 'info', 'xspf.info')
        jspf_to_calliope(track, entry, 'image', 'image')
        jspf_to_calliope(track, entry, 'album', 'album')
        jspf_to_calliope(track, entry, 'trackNum', 'album.track-number')
        jspf_to_calliope(track, entry, 'duration', 'duration')

        if 'duration' in entry:
            # Convert from milliseconds to seconds.
            entry['duration'] = int(entry['duration']) / 1000.0

        # We currently ignore the <link>, <meta> and <extension> tags.

        if len(entry) == 0:
            log.warn("Empty 'track' entry found.")

        entries.append(entry)

    if len(entries) > 0:
        # If the playlist has metadata tags, we store them on the first entry
        # that we return.
        metadata_entry = entries[0]
        jspf_to_calliope(playlist, metadata_entry, 'title', 'playlist.title')
        jspf_to_calliope(playlist, metadata_entry, 'creator', 'playlist.creator')
        jspf_to_calliope(playlist, metadata_entry, 'annotation', 'playlist.annotation')
        jspf_to_calliope(playlist, metadata_entry, 'info', 'playlist.info')
        jspf_to_calliope(playlist, metadata_entry, 'location', 'playlist.location')
        jspf_to_calliope(playlist, metadata_entry, 'identifier', 'playlist.identifier')
        jspf_to_calliope(playlist, metadata_entry, 'image', 'playlist.image')
        jspf_to_calliope(playlist, metadata_entry, 'date', 'playlist.date')
        jspf_to_calliope(playlist, metadata_entry, 'license', 'playlist.license')

        # We currently ignore the <attribution> and <link> tags.

    return entries


def import_(text):
    playlist_format = guess_format(text)

    if not playlist_format:
        raise RuntimeError("Could not determine the input format.")
    elif playlist_format == PlaylistFormat.PLS:
        entries = parse_pls(text)
    elif playlist_format == PlaylistFormat.XSPF:
        entries = parse_xspf(text)
    elif playlist_format == PlaylistFormat.JSPF:
        entries = parse_jspf(text)

    return entries
