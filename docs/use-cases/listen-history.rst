.. _listen_history:

Analysing your listen history
==================================

The ``cpe lastfm-history`` command can provide a record of songs that you have
listened to. It has some tools to help analyse this data as well.

Artists which you discovered this year
-------------------------------------

.. code:: bash

   cpe lastfm-history artists --first-play-since='1 year ago'

You may want to use `--min-listens=3` to filter out things you only played once
or twice.

Music which you haven't listened to for over a year
---------------------------------------------------

Start with this command:

.. code:: bash

   cpe lastfm-history tracks --last-play-before='1 year ago'

This gives you a raw list of tracks.

Perhaps some of these tracks haven't been played in a long time because you
don't like them.

You might add ``--min-listens=5`` to remove tracks that you
didn't play many times to reduce the size of the list.

You can select tracks from your local collection that you didn't listen to
in over a year using this command:

.. code:: bash

   cpe lastfm-history tracks --last-play-before='1 year ago' --min-listens=5 | cpe tracker annotate - | jq 'select(.["tracker.url"])'
