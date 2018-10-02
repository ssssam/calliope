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

Look in the `docs/` subdirectory for a list of example use cases for
Calliope. This is not an exhaustive list -- many more things are possible.
