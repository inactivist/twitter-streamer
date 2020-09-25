"""Config utilities and variables.
"""
import configparser


class DictConfigParser(configparser.ConfigParser):
    """Provides dictionary access to ConfigParser items.

    Inspired by http://stackoverflow.com/a/3220891/1309774
    """
    def __init__(self):
        configparser.ConfigParser.__init__(self)
        self.optionxform = str

    def as_dict(self):
        d = dict(self._sections)
        for k in d:
            d[k] = dict(self._defaults, **d[k])
            d[k].pop('__name__', None)
        return d
