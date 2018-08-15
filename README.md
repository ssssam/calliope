```
  oooooooo8             o888  o888  o88
o888     88   ooooooo    888   888  oooo   ooooooo  ooooooooo    ooooooooo8
888           ooooo888   888   888   888 888     888 888    888 888oooooo8
888o     oo 888    888   888   888   888 888     888 888    888 888
 888oooo88   88ooo88 8o o888o o888o o888o  88ooo88   888ooo88     88oooo888
                                                    o888
```

Calliope provides various utilities for working with playlists and
collections of music.

# The basics

All Calliope commands operate on *playlists*, which are represented as text.
Here is an example of a simple Calliope playlist:

    - artist: The Mighty Mighty Bosstones
      track: The Impression That I Get
    - artist: Less Than Jake
      track: Gainesville Rock City

This playlist uses a standard format called [YAML](http://yaml.org/) which is
simple for people to read and write. The Calliope tools don't understand this
format directly, instead they use a simpler format called
[JSON](https://json.org/). It's simple to convert between the two formats using
a tool called [yq](https://github.com/kislyuk/yq).

Calliope commands are designed to be combined with each other, with the
data processing tools [jq](https://stedolan.github.io/jq/) and
[yq](https://github.com/kislyuk/yq), and with other UNIX shell tools.
Most commands default to reading playlists on stdin and writing processed
playlists on stdout.

Run `cpe` to see the list of commands available.

# Use cases

## Copying music onto a portable device

You can copy a playlist from one device to another by creating a .playlist file, then using `cpe sync`.

Start by writing a playlist as a .yaml file. If you don't want to fill in the
`location` fields yourself you can pipe the playlist to `cpe tracker` to find
the files for you.

Then copy the files to the device:

     cpe sync ./my.playlist --target /path/to/device

You can pass extra options to `cpe sync` to enable transcoding and/or renaming
of the files, see `cpe sync --help` for details.

## Creating mixes

You can use Calliope to create simple audio mixes.

Start by writing a playlist as a .yaml file. If you don't want to fill in the
`location` fields yourself you can pipe the playlist to `cpe tracker` to find
the files for you.

Alternately, you can create a playlist in Rhythmbox, export it to a `.pls` file
and then pipe to `cpe import` to convert to Calliope format.

Then pipe the playlist to `cpe play -o mix.wav`. You will get all the tracks
mixed into a single audio file named `mix.wav`. On stdout you will get the
playlist with extra `start-time` fields, which can be piped to `cpe export` to
create a CUE sheet for the mix.
