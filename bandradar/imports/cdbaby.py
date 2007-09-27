from BeautifulSoup import BeautifulSoup as bs
from datetime import date
import urllib
import re

baseurl = "http://cdbaby.com"
affiliate_extension = "/from/bandradar"

def recordings(name):
    """return names of albums by a given artist on cdbaby"""
    name = urllib.quote_plus(name.encode('utf8'))
    url = baseurl + "/found?artist=" + name
    usock = urllib.urlopen(url)
    soup = bs(usock.read())
    albumlist = soup.find('ul', "albumlist")
    if not albumlist or not albumlist.previousSibling.string.startswith("Exact"):
        return
    albums = albumlist.findAll('div', "albumbox")
    for album in albums:
        a = {}
        a['name'] = album.a['title'].split(": ")[1]
        a['url'] = baseurl + album.a['href'] + affiliate_extension
        a['img_url'] = album.a.img['src']
        yield a

if __name__ == "__main__":
    print list(recordings("the whispers"))
