from BeautifulSoup import BeautifulSoup as bs
from datetime import date
import urllib
import re

baseurl = "http://cdbaby.com"

def recordings(name):
    """return names of albums by a given artist on cdbaby"""
    name = name.replace(" ", "+")
    url = baseurl + "/found?artist=" + name
    print url
    usock = urllib.urlopen(url)
    soup = bs(usock.read())
    albumlist = soup.find('ul', "albumlist")
    if not albumlist:
        return
    albums = albumlist.findAll('div', "albumbox")
    for album in albums:
        a = {}
        a['name'] = album.a['title'].partition(": ")[2]
        a['url'] = baseurl + album.a['href']
        a['img_url'] = album.a.img['src']
        yield a


if __name__ == "__main__":
    print list(albums("the whispers"))
