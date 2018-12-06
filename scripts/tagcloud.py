import json
import sys

import calliope

tags = {}

for item in calliope.playlist.read(sys.stdin):
    artist_name = item['artist']
    artist_tags = item['lastfm.tags.top']
    for tag in artist_tags:
        l = tags.get(tag, set())
        l.add(artist_name)
        tags[tag] = l


output = []
for tag, artists in tags.items():
    output.append({'text': tag, 'weight': len(artists)})

output = sorted(output, key=lambda item: item['weight'], reverse=True)

json.dump(output[:100], sys.stdout)
