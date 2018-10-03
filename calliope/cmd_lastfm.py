#!/usr/bin/env python3
# Calliope
# Copyright (C) 2018  Sam Thursfield <sam@afuera.me.uk>
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


import lastfmclient

import click

import hashlib
import logging
import os
import sys
import warnings

import calliope

log = logging.getLogger(__name__)


def sha1sum(text):
    sha1 = hashlib.sha1()
    sha1.update(text.encode('utf-8'))
    return sha1.hexdigest()


def parse_response_code(url):
    '''Parse the response code in the given response url'''

    try:
        return url.split("?token=")[1].split("&")[0]
    except IndexError:
        return None


def prompt_for_user_token(username, client_id=None, client_secret=None,
                          redirect_uri=None):
    '''Prompt user to obtain authorization token.'''

    # Modelled on similar code in Spotipy: https://github.com/plamere/spotipy

    if not client_id:
        client_id = os.getenv('LASTFM_CLIENT_ID')

    if not client_secret:
        client_secret = os.getenv('LASTFM_CLIENT_SECRET')

    if not redirect_uri:
        redirect_uri = os.getenv('LASTFM_REDIRECT_URI')

    if not client_id:
        print("""
            You need to set your LastFM API credentials. You can do this by
            setting environment variables like so:

            export LASTFM_CLIENT_ID='your-lastfm-client-id'
            export LASTFM_CLIENT_SECRET='your-lastfm-client-secret'
            export LASTFM_REDIRECT_URI='your-app-redirect-url'

            Get your credentials at     
                https://www.last.fm/api/account/create
        """)
        raise RuntimeError("No credentials set")

    print("""

        User authentication requires interaction with your
        web browser. Once you enter your credentials and
        give authorization, you will be redirected to
        a url.  Paste that url you were directed to to
        complete the authorization.

    """)
    lastfm = lastfmclient.LastfmClient(api_key=client_id,
                                        api_secret=client_secret)
    auth_url = lastfm.get_auth_url(redirect_uri)
    try:
        import webbrowser
        webbrowser.open(auth_url)
        print("Opened %s in your browser" % auth_url)
    except:
        print("Please navigate here: %s" % auth_url)

    print("\n")

    try:
        response = raw_input("Enter the URL you were redirected to: ")
    except NameError:
        response = input("Enter the URL you were redirected to: ")

    print("\n")

    token = parse_response_code(response)

    return token


def add_lastfm_artist_top_tags(lastfm, cache, item):
    artist_name = item['artist']

    found, entry = cache.lookup('artist-top-tags:{}'.format(artist_name))

    if found:
        log.debug("Found artist-top-tags:{} in cache".format(artist_name))
    else:
        log.debug("Didn't find artist-top-tags:{} in cache, running remote query".format(artist_name))

        try:
            entry = lastfm.artist.get_top_tags(artist_name)
        except lastfmclient.exceptions.InvalidParametersError:
            warnings = item.get('lastfm.warnings', [])
            warnings += ["Unable to find artist on Last.fm"]
            item['lastfm.warnings'] = warnings
            entry = None

        cache.store('artist-top-tags:{}'.format(artist_name), entry)

    if entry is not None and 'tag' in entry:
        item['lastfm.tags.top'] = [tag['name'] for tag in entry['tag']]

    return item


@calliope.cli.group(name='lastfm',
                    help="Interface to the Last.fm music database")
@click.option('--user', metavar='NAME',
              help="show data for the given Last.fm user")
@click.pass_context
def lastfm_cli(context, user):
    if not user:
        user = calliope.config.get('lastfm', 'user')
    if not user:
        raise RuntimeError("Please specify a username.")

    context.obj.user = user
    log.debug("LastFM user: {}".format(user))

    if 'CALLIOPE_TEST_ONLY' in os.environ:
        sys.exit(0)

    client_id = calliope.config.get('lastfm', 'client-id')
    client_secret = calliope.config.get('lastfm', 'client-secret')
    redirect_uri = calliope.config.get('lastfm', 'redirect-uri')

    cache = calliope.cache.Cache('lastfm')

    lastfm = lastfmclient.LastfmClient(
        api_key=client_id,
        api_secret=client_secret)

    session_key_cache_id = sha1sum(client_id + client_secret + redirect_uri + user)
    found, session_key = cache.lookup('key.%s' % session_key_cache_id)

    if not found:
        token = prompt_for_user_token(user, client_id, client_secret,
                                      redirect_uri)

        session_key = lastfm.auth.get_session(token)
        cache.store('key.%s' % session_key_cache_id, session_key)

    log.debug("LastFM session key: {}".format(session_key))
    lastfm.session_key = session_key

    context.obj.lastfm = lastfm


@lastfm_cli.command(name='annotate-tags')
@click.argument('playlist', type=click.File(mode='r'))
@click.pass_context
def annotate_tags(context, playlist):
    '''Annotate playlist with tags from Last.fm'''

    lastfm = context.obj.lastfm
    cache = calliope.cache.Cache(namespace='lastfm')

    for item in calliope.playlist.read(playlist):
        if 'artist' in item and 'last.fm.tags' not in item:
            try:
                item = add_lastfm_artist_top_tags(lastfm, cache, item)
            except RuntimeError as e:
                raise RuntimeError("%s\nItem: %s" % (e, item))
        calliope.playlist.write([item], sys.stdout)


@lastfm_cli.command(name='top-artists')
@click.pass_context
@click.option('-c', '--count', type=int, default=20,
              help="Maximum number of artists to return")
@click.option('--time-range', default='overall',
              type=click.Choice(['overall', '7day', '1month', '3month',
                                 '6month', '12month']))
@click.option('--include', '-i', type=click.Choice(['images']), multiple=True)
def cmd_top_artists(context, count, time_range, include):
    '''Return user's top artists.'''
    lastfm = context.obj.lastfm
    response = lastfm.user.get_top_artists(user=context.obj.user, limit=count, period=time_range)

    output = []
    for artist_info in response['artist']:
        output_item = {
            'artist': artist_info['name'],
            'musicbrainz.artist': artist_info['mbid'],
            'lastfm.url': artist_info['url'],
            'lastfm.playcount': artist_info['playcount'],
            'lastfm.user-ranking': artist_info['@attr']['rank'],
        }

        if 'images' in include:
            output_item['lastfm.images'] = artist_info['image']

        output.append(output_item)

    calliope.playlist.write(output, sys.stdout)
