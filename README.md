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

Run `cpe` to see the list of commands available.

Most commands operate on *playlists*. Calliope defines a way of representing
playlists as [YAML](http://yaml.org/) documents. Here's a minimal example:

    name: Minimal example
    playlist:
    - artist: The Mighty Mighty Bosstones
      track: The Impression That I Get
    - artist: Less Than Jake
      track: Gainesville Rock City

You can also create *collections*, which are represented similarly to playlists
but are conceptually different as they represent an unordered collection of
tracks, rather than an ordered list.

The Calliope playlist format aims to be arbitrarily extensible so that any kind
of data can be carried along with the tracks.

Some standard fields that Calliope uses are:

  * `location`: a URL where a track can be accessed.

Calliope commands are designed to be combined with each other and with other
UNIX shell tools. Most commands default to reading playlists on stdin and
writing processed playlists on stdout.

# Use cases

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
