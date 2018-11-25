Copying music onto a portable device
====================================

You can copy a playlist from one device to another by creating a .playlist file, then using `cpe sync`.

Start by writing a playlist as a .yaml file. If you don't want to fill in the
``location`` fields yourself you can pipe the playlist to ``cpe tracker`` to find
the files for you.

Then copy the files to the device:

.. code:: bash

     cpe sync ./my.playlist --target /path/to/device

You can pass extra options to ``cpe sync`` to enable transcoding and/or renaming
of the files, see ``cpe sync --help`` for details.
