What music should I buy next?
=============================

Your local music collection might not contain all the music that you listen
to. You can use Calliope to find tracks that you listen to online but don't
have available locally. Here is an example.

.. code:: bash

    cpe diff <(cpe lastfm-history tracks --min-listens 4) <(cpe tracker local-tracks)
