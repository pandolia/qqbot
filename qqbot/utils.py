# -*- coding: utf-8 -*-

import json, ConfigParser

JsonLoads = lambda s: encJson(json.loads(s))
JsonDumps = json.dumps

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
    
    def items(self, section):
        if not self.has_section(section):
            return []
        else:
            return ConfigParser.ConfigParser.items(self, section)

def Utf8Partition(msg, n):
    if n >= len(msg):
        return msg, ''
    else:
        # All utf8 characters start with '0xxx-xxxx' or '11xx-xxxx'
        while n > 0 and ord(msg[n]) >> 6 == 2:
            n -= 1
        return msg[:n], msg[n:]