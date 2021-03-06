Follow your top artists on Twitter
==================================

First you need to get a list of your :ref:`most listened artists <top_artists>`.

Now pipe that list to ``cpe musicbrainz --include urls`` and you'll get a list
of relationship URLs for each artist.

Finally, pipe that into ``jq``:

.. code:: bash

    jq '. | ."musicbrainz.artist.urls" // [] | .[]."musicbrainz.url.target" | "@" + match("^http[s]?://(www\\\.)?twitter.com/(.*)").captures[1].string' -r |sort -u

Now you have a list of Twitter handles. Using a tool such as
`[t (Twitter CLI) <https://github.com/sferik/t>`_ you can add all these handles
to a list, or you can just follow all of them directly. Note that you have to
fill in a bunch of forms in order to get a Twitter API key before you can use a
Twitter CLI tool. The ``t authorize`` command will point you in the right
direction.
