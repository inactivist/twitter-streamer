"""
Filter tweet JSON data from twitter-streamer.py by location.
This is necessary because Twitter's streaming API locations filter
has some limitations, in that you can't filter on a very small
region.
"""
import sys
import logging
import simplejson as json
import argparse

logging.basicConfig()
logger = logging.getLogger(__name__)

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
        try:
            bbox = t['place']['bounding_box']['coordinates'][0][0]
            return bbox
        except KeyError:
            pass
    return None


def point_in_bbox(point, bbox):
    """ Return True if point is in bbox.

        bbox is tuple with long, lat, long, lat where SW corner is first, NE corner is second.
        point is tuple(long,lat)

    """
    #print point, bbox
    return point[0] >= bbox[0] and point[0] <= bbox[2] and \
        point[1] >= bbox[1] and point[1] <= bbox[3]


def four_floats(vals):
    bbox = [float(x) for x in vals.split()]
    if len(bbox) != 4:
        raise argparse.ArgumentTypeError('Bounding box must contain exactly four floating-point values.')
    if bbox[0] > bbox[2] or bbox[1] > bbox[3]:
        raise argparse.ArgumentTypeError('Bounding box must be in the form of minlon minlat maxlon maxlat.')
    return bbox

parser = argparse.ArgumentParser()
parser.add_argument('bbox',
    metavar='bounding-box',
    type=four_floats)

opts = parser.parse_args()

# Get bounding box coordinates (minlon, minlat, maxlon, maxlat)

def output(opts, line, json_obj):
    print line

for line in sys.stdin:
    try:
        line = line.strip()
        t = json.loads(line)
        loc = get_coords(t)
        if loc:
            id_str = t['id_str']
            inside = point_in_bbox(loc, opts.bbox)
            if inside:
                output(opts, line, t)
    except Exception:
        logger.exception("Error parsing line %s" % line)
