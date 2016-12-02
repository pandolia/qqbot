# -*- coding: utf-8 -*-

import json

def jsonLoad(filename):
    with open(filename, 'r') as f:
        return encJson(json.loads(f.read()))

def jsonLoads(s):
    return encJson(json.loads(s))

jsonDumps = json.dumps

def encJson(obj):
    if hasattr(obj, 'encode'):
        return obj.encode('utf8')
    elif isinstance(obj, list):
        return [encJson(e) for e in obj]
    elif isinstance(obj, dict):
        return dict((encJson(k), encJson(v)) for k,v in obj.iteritems())
    else:
        return obj
