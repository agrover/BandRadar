import urllib
import import_util

baseurl = "http://cdbaby.com"
affiliate_extension = "/from/bandradar"

def recordings(name):
    """return names of albums by a given artist on cdbaby"""
    quoted_name = urllib.quote_plus(name.encode('utf8'))
    url = baseurl + "/found?artist=" + quoted_name
    try:
        soup = import_util.url_to_soup(url)
    except:
        return
    albumlist = soup.find('ul', "albumlist")
    if not albumlist or not albumlist.previousSibling.string.startswith("Partial"):
        return
    albums = albumlist.findAll('div', "albumbox")
    for album in albums:
        a = {}
        artist_name = import_util.unescape(album.a['title'].split(": ", 1)[0])
        a['name'] = import_util.unescape(album.a['title'].split(": ", 1)[1])
        a['url'] = baseurl + album.a['href'] + affiliate_extension
        a['img_url'] = album.a.img['src']
        if artist_name.lower() == name.lower():
            yield a

if __name__ == "__main__":
    print list(recordings("the whispers"))
