.. _selecting:

Selecting music from a collection
=================================

Selecting similar music to a given track
----------------------------------------

Some online services provide 'similar artist'data. You can use this to
select music from a collection that has similarity to a given 'seed'.

For example, if I want to create a playlist from my music collection
that was similar in style to the band beNUTS, I can do this:

.. code:: bash

   cpe lastfm similar-artists benuts | cpe tracker expand-tracks | cpe shuffle

Here's a similar example that looks at the now-playing track in the Rhythmbox
music player and enqueues some similar tracks:

.. code:: bash

   cpe lastfm similar-tracks "$(rhythmbox-client --print-playing-format %ta)" "$(rhythmbox-client --print-playing-format %tt)" |
     cpe tracker annotate - | jq 'select(.["tracker.url"]) | .["tracker.url"]' | xargs rhythmbox-client --enqueue
