# Calliope -- last.fm miner
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


import logging
import os

from miners.lastfm import lastexport


# FIXME: need to add 'accounts' info.
USERNAME = 'ssam'


log = logging.getLogger(__name__)


def escape_for_lastfm_uri(name):
    # I've attempted to use the same rule here as lastfm use for the
    # http://last.fm/music/... URLs. Which appears to be simply the
    # following:
    return name.replace(' ', '+').replace(':', '%2F')


class LastfmMiner:
    def __init__(self, store):
        self.store = store

    def migrations_dir(self):
        return os.path.join(os.path.dirname(__file__), 'migrations')

    def sync(self, full=False):
        # FIXME: This currently won't take any notice if a track is *removed*
        # from the user's last.fm history. The 'full' sync mode needs to check
        # for that. Currently you just need to not listen to rubbish music that
        # you'll subsequently become embarrassed about.

        cursor = self.store.cursor()

        stored_plays_sql = 'SELECT COUNT(id) FROM imports_lastfm'
        stored_plays = cursor.execute(stored_plays_sql).fetchone()[0]

        newest_play_sql = \
            'SELECT plays.datetime ' \
            'FROM imports_lastfm INNER JOIN plays ' \
            'WHERE plays.id = imports_lastfm.play_id ' \
            'ORDER BY plays.datetime ' \
            'LIMIT 1'
        newest_play = cursor.execute(newest_play_sql).fetchone()[0] or 0
        log.debug("Newest play: %i", newest_play)

        gen = lastexport.get_tracks('last.fm', USERNAME,
                                    tracktype='recenttracks')

        page_size = None
        for page, total_pages, tracks in gen:
            log.debug("Received page %i/%i", page, total_pages)
            top_datetime = int(tracks[0][0])

            page_size = page_size or len(tracks)

            if top_datetime < newest_play:
                if stored_plays >= page_size * total_pages:
                    log.debug(
                        "Scrobble %i is older than newest play. We have %i "
                        "stored plays and lastfm seems to have %i total "
                        "plays. This non-full import is complete.",
                        top_datetime, stored_plays, page_size * total_pages)
                    break

            for scrobble in tracks:
                self.intern_scrobble(scrobble)
            self.store.commit()

        self.store.commit()

    def intern_scrobble(self, play_info):
        datetime, trackname, artistname, albumname, trackmbid, artistmbid, \
            albummbid = play_info
        uri = 'lastfm://%s/%s/' % (escape_for_lastfm_uri(artistname),
                                   escape_for_lastfm_uri(trackname))
        item_id = self.store.intern_item(uri, trackmbid)
        play_id = self.store.intern_play(datetime, item_id)

        cursor = self.store.cursor()
        find_lastfm_sql = 'SELECT id FROM imports_lastfm WHERE play_id = ?'
        row = cursor.execute(find_lastfm_sql, [play_id]).fetchone()
        if row is None:
            cursor.execute(
                'INSERT INTO imports_lastfm(play_id, trackname, '
                ' artistname, albumname, trackmbid, artistmbid, '
                ' albummbid) VALUES (?, ?, ?, ?, ?, ?, ?)', [play_id,
                trackname, artistname, albumname, trackmbid, artistmbid,
                albummbid])
            scrobble_id = cursor.lastrowid
        else:
            scrobble_id = row[0]
        return scrobble_id


def load(store):
    miner = LastfmMiner(store)
    store.apply_migrations('miner.lastfm', miner.migrations_dir())
    return miner
