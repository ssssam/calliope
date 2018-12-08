# Calliope -- last.fm history
# Copyright (C) 2015,2018  Sam Thursfield <sam@afuera.me.uk>
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


import xdg.BaseDirectory
import yoyo

import logging
import os
import re
import sqlite3
import time

import calliope.lastfm.lastexport

log = logging.getLogger(__name__)


_escape_re = re.compile('[^a-zA-Z0-9]')
def escape_for_sql_identifier(name):
    return re.sub(_escape_re, '_', name)


class Store:
    def __init__(self, file_path):
        self.db = sqlite3.connect(file_path)
        self.apply_migrations(file_path, self.migrations_dir())

    def migrations_dir(self):
        return os.path.join(os.path.dirname(__file__), 'migrations')

    def apply_migrations(self, file_path, migrations_path):
        backend = yoyo.get_backend('sqlite:///' + file_path)
        migrations = yoyo.read_migrations(migrations_path)
        with backend.lock():
            backend.apply_migrations(backend.to_apply(migrations))

    def commit(self):
        retries = 3
        for i in range(0, retries):
            try:
                self.db.commit()
                break
            except sqlite3.OperationalError as e:
                # Probably 'database is locked', we should retry a few times.
                logging.debug("%s, try %i of %i", e, i, retries)
                if i == retries:
                    raise
                else:
                    time.sleep(0.1)
                    pass

    def cursor(self):
        return self.db.cursor()


def escape_for_lastfm_uri(name):
    # I've attempted to use the same rule here as lastfm use for the
    # http://last.fm/music/... URLs. Which appears to be simply the
    # following:
    return name.replace(' ', '+').replace(':', '%2F')


class _LastfmHistory:
    def __init__(self, store, username):
        self.store = store
        self.username = username

    def migrations_dir(self):
        return os.path.join(os.path.dirname(__file__), 'migrations')

    def _count_stored_plays(self, cursor):
        stored_plays_sql = 'SELECT COUNT(id) FROM imports_lastfm'
        return cursor.execute(stored_plays_sql).fetchone()[0]

    def _get_newest_play_datetime(self, cursor):
        newest_play_sql = \
            'SELECT datetime FROM imports_lastfm ORDER BY datetime DESC LIMIT 1'
        result = cursor.execute(newest_play_sql).fetchone()
        if result:
            return result[0]
        else:
            return 0

    def sync(self, full=False):
        # FIXME: This currently won't take any notice if a track is *removed*
        # from the user's last.fm history. The 'full' sync mode needs to check
        # for that. Currently you just need to not listen to rubbish music that
        # you'll subsequently become embarrassed about.

        cursor = self.store.cursor()

        stored_plays = self._count_stored_plays(cursor)
        newest_play = self._get_newest_play_datetime(cursor)

        log.debug("Newest play: %i", newest_play)

        gen = calliope.lastfm.lastexport.get_tracks(
            'last.fm', self.username, tracktype='recenttracks')

        page_size = None
        total_pages = 0
        for page, total_pages, tracks in gen:
            if tracks is None:
                # This can happen when a fetch request times out.
                # The 'lastexport' will eventually raise an exception
                # after retrying a few times.
                continue

            log.debug("Received page %i/%i", page, total_pages)
            top_datetime = int(tracks[0][0])

            page_size = page_size or len(tracks)

            if top_datetime <= newest_play:
                log.debug("Caught up with stored plays.")
                break

            for scrobble in tracks:
                self.intern_scrobble(scrobble)
            self.store.commit()

        last_stored_page = stored_plays / page_size
        if last_stored_page < total_pages - 1:
            log.debug('Processing missing history from page %i/%i',
                      last_stored_page, total_pages)
            gen = calliope.lastfm.lastexport.get_tracks(
                'last.fm', self.username, tracktype='recenttracks',
                startpage=last_stored_page)

            for page, total_pages, tracks in gen:
                log.debug("Received page %i/%i", page, total_pages)
                for scrobble in tracks:
                    self.intern_scrobble(scrobble)
                self.store.commit()

    def intern_scrobble(self, play_info):
        datetime, trackname, artistname, albumname, trackmbid, artistmbid, \
            albummbid = play_info
        uri = 'lastfm://%s/%s/' % (escape_for_lastfm_uri(artistname),
                                   escape_for_lastfm_uri(trackname))

        cursor = self.store.cursor()
        find_lastfm_sql = 'SELECT id FROM imports_lastfm ' \
                          '  WHERE datetime = ? AND trackname = ? AND artistname = ?'
        row = cursor.execute(find_lastfm_sql, [datetime, trackname, artistname]).fetchone()
        if row is None:
            cursor.execute(
                'INSERT INTO imports_lastfm(datetime, trackname, '
                ' artistname, albumname, trackmbid, artistmbid, '
                ' albummbid) VALUES (?, ?, ?, ?, ?, ?, ?)',
                [datetime, trackname, artistname, albumname, trackmbid,
                 artistmbid, albummbid])
            scrobble_id = cursor.lastrowid
        else:
            scrobble_id = row[0]
        return scrobble_id

    def scrobbles(self):
        '''Return individual scrobbles as a Calliope playlist.'''
        sql = 'SELECT datetime, trackname, artistname, albumname, ' + \
              ' trackmbid, artistmbid, albummbid FROM imports_lastfm ' + \
              ' ORDER BY datetime DESC'
        cursor = self.store.cursor()
        cursor.execute(sql)
        for row in cursor:
            datetime, trackname, artistname, albumname, trackmbid, \
                artistmbid, albummbid = row
            item = {
                'artist': artistname,
                'album': albumname,
                'track': trackname,
                'lastfm.scrobble_datetime': datetime
            }
            if artistmbid:
                item['musicbrainz.artist'] = artistmbid
            if albummbid:
                item['musicbrainz.album'] = albummbid
            if trackmbid:
                item['musicbrainz.track'] = trackmbid
            yield item

    def tracks(self, min_listens=1):
        '''Return tracks from the lastfm history.'''
        # last.fm doesn't give us a single unique identifier for the tracks, so
        # we construct one by concatenating the two fields that are guaranteed
        # to be present for every track (which are 'artistname' and 'trackname').
        sql = 'SELECT COUNT(trackid) AS playcount, trackname, artistname, albumname, ' + \
              '       artistmbid, trackmbid, albummbid ' + \
              '  FROM ( SELECT (artistname || \',\' || trackname) AS trackid, trackname, artistname, ' + \
              '                albumname, trackmbid, artistmbid, albummbid ' + \
              '           FROM imports_lastfm ) ' + \
              '  GROUP BY trackid HAVING playcount > ? ' + \
              '  ORDER BY trackid';
        cursor = self.store.cursor()
        cursor.execute(sql, [min_listens])
        for row in cursor:
            playcount, trackname, artistname, albumname, trackmbid, \
                artistmbid, albummbid = row
            item = {
                'artist': artistname,
                'album': albumname,
                'track': trackname,
                'lastfm.playcount': playcount
            }
            if artistmbid:
                item['musicbrainz.artist'] = artistmbid
            if albummbid:
                item['musicbrainz.album'] = albummbid
            if trackmbid:
                item['musicbrainz.track'] = trackmbid
            yield item


def load(username, cachedir=None):
    if cachedir is None:
        cachedir = xdg.BaseDirectory.save_cache_path('calliope')

    namespace = 'lastfm-history.%s' % username

    store_path = os.path.join(cachedir, namespace) + '.sqlite'
    store = Store(store_path)

    history = _LastfmHistory(store, username)
    return history
