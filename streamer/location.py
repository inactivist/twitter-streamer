import logging

import tweepy

logger = logging.getLogger(__name__)

"""
    List of named location query (--location-query) names and their
    associated bounding boxes (longitude, latitude) (what is the name of that standard?  geoJSON?)

    Recursive lookups:
    If a value is string, it's a reference to a named entry in the table.  Use the remainder of the
    value string as the new lookup key.
"""
LOCATION_QUERY_MACROS = {
    "any": [-180, -90, 180, 90],
    "all": "any",
    "global": "any",
    "usa": [
        -124.848974,
        24.396308,
        -66.885444,
        49.384358,
    ],  # http://www.openstreetmap.org/?box=yes&bbox=-124.848974,24.396308,-66.885444,49.384358
    "contintental_usa": "usa",
}


def lookup_location_query_macro(name):
    """
    Look up location query name in macro table.
    Return list of coordinates of bounding box as floating point numbers, or None if
    not found.
    """
    resolved = LOCATION_QUERY_MACROS.get(name.lower())
    if isinstance(resolved, str):
        return lookup_location_query_macro(resolved)
    return resolved


def location_query_to_location_filter(tweepy_auth, location_query):
    t = lookup_location_query_macro(location_query)
    if t:
        return t
    api = tweepy.API(tweepy_auth)
    # Normalize whitespace to single spaces.
    places = api.geo_search(query=location_query)
    normalized_location_query = location_query.replace(" ", "")
    for place in places:
        logger.debug('Considering place "%s"' % place.full_name)
        # Normalize spaces
        if (
            place.full_name.replace(" ", "").lower()
            == normalized_location_query.lower()
        ):
            logger.info(
                "Found matching place: full_name=%(full_name)s id=%(id)s url=%(url)s"
                % place.__dict__
            )
            if place.bounding_box is not None:
                t = [x for x in place.bounding_box.origin()]
                t.extend([x for x in place.bounding_box.corner()])
                logger.info("  location box: %s" % t)
                return t
            else:
                raise ValueError(
                    "Place '%s' does not have a bounding box." % place.full_name
                )

    # Nothing found, try for matching macro
    raise ValueError("'%s': No such place." % location_query)
