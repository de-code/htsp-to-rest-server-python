import unicodedata
import collections

def unicode_to_string1(s):
    return unicodedata.normalize('NFKD', s).encode('ascii','ignore')

def unicode_to_string(data):
    if isinstance(data, basestring):
        return str(data)
    elif isinstance(data, collections.Mapping):
        return dict(map(unicode_to_string, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(unicode_to_string, data))
    else:
        return data
