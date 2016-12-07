# -*- coding: utf-8 -*-

import json, ConfigParser

jsonLoads = lambda s: encJson(json.loads(s))
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

class MConfigParser(ConfigParser.ConfigParser):
    def get(self, section, option, default=None):
        try:
            return ConfigParser.ConfigParser.get(self, section, option)
        except ConfigParser.NoSectionError:
            self.add_section(section)
        except ConfigParser.NoOptionError:
            pass
        self.set(section, option, default)
        return default
