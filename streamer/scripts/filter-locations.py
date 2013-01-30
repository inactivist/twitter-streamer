"""
Filter tweet JSON data from twitter-streamer.py by location.
This is necessary because Twitter's streaming API locations filter
has some limitations, in that you can't filter on a very small
region.
"""
import sys
import simplejson as json
import argparse

def get_coords(t):
    """ Get best coordinates for a tweet.
        Use same scheme as Twitter API docs.
        Prefer, in this order:
          1. coordinates.coordinates [long, lat]
          2. place.bounding_box.coordinates[0][0]

    """
    try:
        # [long, lat]
        c = t['coordinates']
        if c:
            c = c['coordinates']
        return c
    except KeyError:
        bbox = t['place']['bounding_box']['coordinates'][0][0]
        print bbox
        raise
    except KeyError:
        print "None"
        raise


def point_in_bbox(point, bbox):
    """ Return True if point is in bbox.

        bbox is tuple with long, lat, long, lat where SW corner is first, NE corner is second.
        point is tuple(long,lat)

    """
    #print point, bbox
    return point[0] >= bbox[0] and point[0] <= bbox[2] and \
        point[1] >= bbox[1] and point[1] <= bbox[3]


# Get bounding box (minlon, minlat, maxlon, maxlat)
bbox = sys.argv[1].split(',')
assert len(bbox) == 4

for line in sys.stdin:
    try:
        line = line.strip()
        t = json.loads(line)
        loc = get_coords(t)
        if loc and point_in_bbox(loc, bbox):
            #print t['id_str'], loc, bbox #line
            print line

    except json.JSONDecodeError as e:
        sys.stderr.write("Error: %s parsing line %s\n" % (e, line))
        pass
