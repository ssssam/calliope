Playlist format
===============

A playlist entry must have one of the following types:

  * ``type: artist``: A creator of music
  * ``type: track``: An individual piece of music
  * ``type: album``: A release which contains multiple tracks

The ``type`` field doesn't need to be specified explicitly. It can
be inferred based on whether the ``track``, ``album`` or ``artist`` fields
are present.

  * If the ``track`` field is present: the entry is a single piece of music
  * If the ``track`` field is not present but the ``album`` field is present: the entry represents a whole album.
  * If only the ``artist`` field is present: the entry repesents all music by a given artist.

The following fields have specific meanings:

 * ``id``: Unique identifier of the entity.
 * ``artist``: Name of the main 'artist'
 * ``track``: Title of the track.
 * ``album``: Title of the album.

By convention, individual tools should add service-specific fields by prepending
the name of the service and a dot to the fieldname. For example, a track
playcount as reported by lastfm should use the fieldname ``lastfm.playcount``.
