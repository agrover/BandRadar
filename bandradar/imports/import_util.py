from BeautifulSoup import BeautifulSoup as bs
import urllib
import cgi
import htmllib
import StringIO
import gzip

def url_to_soup(url):
    usock = urllib.urlopen(url)
    if usock.headers.get('content-encoding') == 'gzip':
        compressedstream = StringIO.StringIO(usock.read())
        gzipper = gzip.GzipFile(fileobj=compressedstream)
        data = gzipper.read()
    else:
        data = usock.read()
    return bs(data, convertEntities=bs.ALL_ENTITIES)

def stringify(node, children=True):
    """take a beautifulsoup node and flatten it into a string"""
    strings = list()
    for item in node:
        if isinstance(item, basestring):
            strings.append(item)
        else:
            if children:
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

