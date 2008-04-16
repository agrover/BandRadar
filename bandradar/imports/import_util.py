from BeautifulSoup import BeautifulSoup as bs
import urllib
import cgi
import htmllib

def url_to_soup(url):
    usock = urllib.urlopen(url)
    return bs(usock.read(), convertEntities=bs.ALL_ENTITIES)

def stringify(node):
    """take a beautifulsoup node and flatten it into a string"""
    strings = list()
    for item in node:
        if isinstance(item, basestring):
            strings.append(item)
        else:
            for x in stringify(item):
                strings.append(x)
    return "".join(strings)

def escape(text):
    return cgi.escape(text)

def unescape(thing):
    """unescape strings, as well as dicts and lists of strings"""
    if isinstance(thing, dict):
        for name, value in thing.iteritems():
            thing[name] = unescape(value);
    elif isinstance(thing, list):
        thing = [unescape(t) for t in thing]
    elif isinstance(thing, basestring):
        p = htmllib.HTMLParser(None)
        p.save_bgn()
        p.feed(thing)
        thing = p.save_end()
    return thing

