Creating mixes
==============

You can use Calliope to create simple audio mixes.

Start by writing a playlist as a .yaml file. If you don't want to fill in the
``location`` fields yourself you can pipe the playlist to ``cpe tracker annotate``
to find the files for you.

Alternately, you can create a playlist in Rhythmbox, export it to a ``.pls`` file
and then pipe to ``cpe import`` to convert to Calliope format.

Then pipe the playlist to ``cpe play -o mix.wav``. You will get all the tracks
mixed into a single audio file named ``mix.wav``. On stdout you will get the
playlist with extra ``start-time`` fields, which can be piped to ``cpe export`` to
create a CUE sheet for the mix.
