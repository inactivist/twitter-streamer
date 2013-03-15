"""
Some of this code was extracted from other sources.  Copyright information
may be found at the links provided.
"""

def resolve(obj, attrspec):
    """
    Resolve elements from an object.
    Works with objects and dicts.
    From: http://stackoverflow.com/a/9101577/1309774
    """
    for attr in attrspec.split("."):
        try:
            obj = obj[attr]
        except (TypeError, KeyError):
            obj = getattr(obj, attr)
    return obj


def resolve_with_default(obj, attrspec, default=None):
    """
    Resolve elements from an object, with a default value.
    This works with objects AND dicts.
    """
    result = default
    try:
        result = resolve(obj, attrspec)
    except:
        # Pass along the exception if no default is specified; otherwise, eat it.
        if default is None:
            raise
    return result


def multi_getattr(obj, attr, default=None):
    """
    Get a named attribute from an object; multi_getattr(x, 'a.b.c.d') is
    equivalent to x.a.b.c.d. When a default argument is given, it is
    returned when any attribute in the chain doesn't exist; without
    it, an exception is raised when a missing attribute is encountered.

    From http://code.activestate.com/recipes/577346-getattr-with-arbitrary-depth/

    Deprecated, does not work with dictionaries.  Use resolve_with_default()
    instead.
    """
    attributes = attr.split(".")
    for i in attributes:
        try:
            obj = getattr(obj, i)
        except AttributeError:
            if default is not None:
                return default
            else:
                raise
    return obj

def init_logger(logger, level):
    import logging
    FORMAT = "%(asctime)-15s %(message)s"
    logging.basicConfig(format=FORMAT)
    logger.setLevel(level)

