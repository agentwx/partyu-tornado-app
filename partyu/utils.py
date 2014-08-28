# -*- coding: utf-8 -*-
import urllib

def friendly_str(s):
    s = s.encode('utf-8', 'ignore')
    s = urllib.quote_plus(s)
    return s
