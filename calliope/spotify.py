#!/usr/bin/env python3
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

'''calliope-spotify'''

import sys
import os

try:
    import spotipy
    import spotipy.util as util
except ImportError as e:
    print(e)
    print("The 'spotipy' library must be installed to use calliope-spotify.")
    sys.exit(1)


def argument_parser():
    parser = argparse.ArgumentParser(
        description="Import playlists from your Spotify account ")
    parser.add_argument('-d', '--debug', action='store_true',
                        help="enable verbose debug output")

    parser.add_argument('--top', choices=['artists'],
                        help="show the top artists (by number of songs)")

    return parser


def show_tracks(results):
    for i, item in enumerate(tracks['items']):
        track = item['track']
        print("   %d %32.32s %s" % (i, track['artists'][0]['name'], track['name']))


def main():
    args = argument_parser().parse_args()
    if args.debug:
        logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        print("Whoops, need your username!")
        print("usage: python user_playlists.py [username]")
        sys.exit()

    token = util.prompt_for_user_token(username)

    if token:
        top = 40
        sp = spotipy.Spotify(auth=token)
        playlists = sp.user_playlists(username)
        for playlist in playlists['items']:
            if playlist['owner']['id'] == username:
                print()
                print(playlist['name'])
                print('  total tracks', playlist['tracks']['total'])
                results = sp.user_playlist(username, playlist['id'], fields="tracks,next")
                tracks = results['tracks']
                show_tracks(tracks)
                while tracks['next']:
                    tracks = sp.next(tracks)
                    show_tracks(tracks)
    else:
        print("Can't get token for", username)

try:
    main()
except RuntimeError as e:
    sys.stderr.write("ERROR: %s\n" % e)
    sys.exit(1)
