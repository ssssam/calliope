What music from my music collection have I never listened to?
=============================================================

You can find tracks that you have locally but have never listed to by
taking the list of local tracks and subtracting your Last.fm listening history.

.. code:: bash

    cpe diff <(cpe tracker local-tracks) <(cpe lastfm-history tracks)
