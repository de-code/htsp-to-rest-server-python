
def extract(d, keys):
    return dict((k, d[k]) for k in keys if k in d)

def extract_and_map_keys(d, key_map):
    return {key_map[name]: val for name, val in extract(d, key_map.keys()).items()}

def merge(d_default=None, d_override=None):
    if ((d_default == None) and (d_override == None)):
        result = {}
    elif (d_default == None):
        result = d_override
    elif (d_override == None):
        result = d_default
    else:
        result =  dict(d_default.items() + d_override.items())
    return result

def extract_and_merge(d, keys, other=None):
    result = extract(d, keys)
    if (other != None):
        result = dict(other + result)
    return result
