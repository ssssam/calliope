#!/usr/bin/env python3
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


'''calliope-play

Turns a playlist into sounds!

'''


import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst

import yaml

import argparse
import logging
import sys

import calliope


def argument_parser():
    parser = argparse.ArgumentParser(
        description="Play a Calliope playlist or collection")
    parser.add_argument('playlist', nargs='*',
                        help="playlist file")
    parser.add_argument('-d', '--debug', action='store_true',
                        help="enable verbose debug output")

    return parser


def set_element_state_sync(pipeline, target_state):
    bus = pipeline.get_bus()
    pipeline.set_state(target_state)
    while True:
        ret, state, pending = pipeline.get_state(1 * 1000 * 1000 * 1000)
        if ret == Gst.StateChangeReturn.FAILURE:
            msg = bus.pop_filtered(Gst.MessageType.ERROR)
            if msg:
                error = msg.parse_error()
                logging.debug(error.debug)
                raise error.gerror
            else:
                raise RuntimeError("Failed to change state to %s" % target_state)
        if state == target_state:
            break
    logging.debug("Got to state %s", target_state)


def play(playlists):
    '''Play playlists.'''
    file_uris = []
    for playlist_data in playlists:
        for item in calliope.Playlist(playlist_data):
            file_uris.append(item['location'])
    file_uris = list(reversed(file_uris))

    pipeline = Gst.Pipeline.new()
    concat = Gst.ElementFactory.make('concat', 'concat')
    rgvolume = Gst.ElementFactory.make('rgvolume', 'rgvolume')
    audioconvert = Gst.ElementFactory.make('audioconvert', 'audioconvert')
    wavenc = Gst.ElementFactory.make('wavenc', 'wavenc')
    fdsink = Gst.ElementFactory.make('fdsink', 'fdsink')

    for element in [concat, rgvolume, audioconvert, wavenc, fdsink]:
        pipeline.add(element)

    concat.link(audioconvert)
    audioconvert.link(wavenc)
    wavenc.link(fdsink)

    def enqueue_songs(uri_list, i=0):
        uri = uri_list.pop()
        logging.debug("Enqueuing %s", uri)

        uridecodebin = Gst.ElementFactory.make('uridecodebin',
                                               'uridecodebin_%u' % i)
        pipeline.add(uridecodebin)

        uridecodebin.set_property('uri', uri)

        def decode_pad_added(element, pad):
            logging.debug("Pad added")
            pad.link(concat.get_request_pad('sink_%u'))
            if len(uri_list) > 0:
                enqueue_songs(uri_list, i+1)
        uridecodebin.connect('pad-added', decode_pad_added)

    enqueue_songs(file_uris)

    fdsink.set_property('fd', sys.stdout.fileno())

    bus = pipeline.get_bus()

    try:
        set_element_state_sync(pipeline, Gst.State.PLAYING)

        while True:
            message = bus.timed_pop(1 * 1000 * 1000 * 1000)
            if message:
                if message.type == Gst.MessageType.ERROR:
                    error = message.parse_error()
                    logging.debug(error.debug)
                    raise(error.gerror)
                elif message.type == Gst.MessageType.EOS:
                    break
    finally:
        logging.debug("Complete")
        set_element_state_sync(pipeline, Gst.State.NULL)


def main():
    args = argument_parser().parse_args()
    if args.debug:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    if len(args.playlist) == 0:
        input_playlists = yaml.safe_load_all(sys.stdin)
    else:
        input_playlists = (yaml.safe_load(open(playlist, 'r'))
                           for playlist in args.playlist)

    Gst.init()

    play(input_playlists)


try:
    main()
except RuntimeError as e:
    sys.stderr.write("ERROR: %s\n" % e)
    sys.exit(1)
