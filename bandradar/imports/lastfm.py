from BeautifulSoup import BeautifulSoup as bs
from BeautifulSoup import BeautifulStoneSoup as bss
from datetime import date
import urllib
import re

base_url = "http://ws.audioscrobbler.com/1.0/artist/"
lastfm_event_url = "http://www.last.fm/events/?m=Portland&view=c&ofl=Portland%2C+US&&view=a&page="

def artist_info(artist_name, count=3):
    info = dict(img_url=None, similars=[], tags=None)
    if artist_name.find("/") != -1: # can't handle / in name, punt
        return info
    artist_name = urllib.quote_plus(artist_name.encode('utf8'))
    try:
        # get img_url and similars
        usock = urllib.urlopen(base_url + artist_name + "/similar.xml")
        soup = bss(usock.read(), convertEntities=bs.ALL_ENTITIES)
        if str(soup).startswith("No artist"):
            return info
        # lastfm includes a "noimage" link if no img found. don't want!
        if soup.similarartists["picture"].find("noimage") == -1:
            info['img_url'] = urllib.unquote(soup.similarartists["picture"])
        
        info['similars'] = [x.find("name").string for x in soup.findAll("artist")[:count]]

        # get tags
        usock = urllib.urlopen(base_url + artist_name + "/toptags.xml")
        soup = bss(usock.read(), convertEntities=bs.ALL_ENTITIES)
        tags = [x.find("name").string for x in soup.findAll("tag")[:count]]
        tags = [x for x in tags if x.lower().find("seen") == -1]
        if len(tags):
            info['tags'] = " / ".join(tags)[:100]
    finally:
        return info

def events():
    usock = urllib.urlopen(lastfm_event_url + "1")
    soup = bs(usock.read(), convertEntities=bs.ALL_ENTITIES)
    pages =  int(soup("a", attrs={"class":"lastpage"})[0].string)
    for page in range(1, pages+1):
        usock = urllib.urlopen(lastfm_event_url + str(page))
        soup = bs(usock.read(), convertEntities=bs.ALL_ENTITIES)
        for tr in soup("tr", attrs={"class":re.compile("vevent.*")}):
            event_dict = dict(source="lastfm")
            venue = dict()
            venue['name'] = tr("td", attrs={"class":"location adr"})[0].a.strong.string
            day, month, year = tr.attrs[0][1].split("-")[-3:]
            event_dict['date'] = date(int(year), int(month), int(day))
            artists = [tr("td", attrs={"class":"lineup"})[0].a.strong.string]
            try:
                other_artists = tr("td", attrs={"class":"lineup"})[0].a.contents[1].string
                artists.extend(other_artists.split(","))
            except IndexError:
                pass
            event_dict['name'] = ", ".join(artists)
            event_dict['artists'] = artists
            event_dict['venue'] = venue
            yield event_dict

if __name__ == "__main__":
    print user_top_artists("agrover", 4)
    print len(list(events()))
