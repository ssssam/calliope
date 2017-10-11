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


GST_NANOSECONDS = 1 * 1000 * 1000 * 1000


def argument_parser():
    parser = argparse.ArgumentParser(
        description="Play a Calliope playlist or collection")
    parser.add_argument('playlist', nargs='*',
                        help="playlist file")
    parser.add_argument('-d', '--debug', action='store_true',
                        help="enable verbose debug output")
    parser.add_argument('-o', '--output', metavar='FILE', required=True,
                        help="location to write the audio output")

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


def update_item_from_timestamp(item, timestamp):
    item['start-time'] = timestamp / GST_NANOSECONDS
    return item


def update_item_from_tags(item, tags):
    _, artist = tags.get_string('artist')
    if artist:
        item['artist'] = artist
    return item


def play(playlists, audio_output):
    '''Play playlists.'''
    output_playlist = []

    file_uris = []
    for playlist_data in playlists:
        for item in calliope.Playlist(playlist_data):
            file_uris.append(item['location'])
            output_playlist.append(item)
    file_uris = list(reversed(file_uris))

    pipeline = Gst.Pipeline.new()
    concat = Gst.ElementFactory.make('concat', 'concat')
    rgvolume = Gst.ElementFactory.make('rgvolume', 'rgvolume')
    audioconvert = Gst.ElementFactory.make('audioconvert', 'audioconvert')
    wavenc = Gst.ElementFactory.make('wavenc', 'wavenc')
    filesink = Gst.ElementFactory.make('filesink', 'filesink')

    for element in [concat, rgvolume, audioconvert, wavenc, filesink]:
        pipeline.add(element)

    concat.link(audioconvert)
    audioconvert.link(wavenc)
    wavenc.link(filesink)

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

    filesink.set_property('location', audio_output)

    bus = pipeline.get_bus()

    stream_state = {
        'track-index': -1,
        'time': 0
    }

    try:
        set_element_state_sync(pipeline, Gst.State.PLAYING)

        def sync_message_handler(bus, message, _stream_state):
            # We use the sync message handler to get the exact timestamp that
            # each new track begins at.
            if message.type == Gst.MessageType.STREAM_START:
                result, timestamp = pipeline.query_position(Gst.Format.TIME)
                stream_state['track-index'] += 1
                index = stream_state['track-index']
                logging.debug("New stream started. Now at track %i; timestamp %s", index, timestamp)
                update_item_from_timestamp(output_playlist[index], stream_state['time'])
                stream_state['time'] += timestamp

        bus.enable_sync_message_emission()
        bus.connect('sync-message', sync_message_handler, stream_state)

        # This loop processes messages from the GStreamer pipeline while it
        # renders the music.
        while True:
            message = bus.timed_pop(1 * 1000 * 1000 * 1000)
            if message:
                if message.type == Gst.MessageType.ERROR:
                    error = message.parse_error()
                    logging.debug(error.debug)
                    raise(error.gerror)
                elif message.type == Gst.MessageType.EOS:
                    break
                elif message.type == Gst.MessageType.TAG:
                    taglist = message.parse_tag()
                    index = stream_state['track-index']
                    logging.debug("Got new taglist %s at index %i", taglist, index)
                    #logging.debug("Content: %s", taglist.to_string())
                    update_item_from_tags(output_playlist[index], taglist)
    finally:
        logging.debug("Complete")
        set_element_state_sync(pipeline, Gst.State.NULL)

    return output_playlist


def main():
    args = argument_parser().parse_args()
    if args.debug:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    if len(args.playlist) == 0:
        input_playlists = yaml.safe_load_all(sys.stdin)
    else:
        input_playlists = (yaml.safe_load(open(playlist, 'r'))
                           for playlist in args.playlist)

    Gst.init([])

    output_playlist = play(input_playlists, args.output)
    sys.stdout.write(yaml.dump(output_playlist))


try:
    main()
except RuntimeError as e:
    sys.stderr.write("ERROR: %s\n" % e)
    sys.exit(1)
