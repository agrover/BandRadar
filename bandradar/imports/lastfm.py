import scrobxlib
from BeautifulSoup import BeautifulSoup
from datetime import date
import urllib
import re

lastfm_event_url = "http://www.last.fm/events/?m=Portland&view=c&ofl=Portland%2C+US&&view=a&page="

def user_top_artists(user_name, limit=10):
    return [artist['name'] for artist in scrobxlib.topArtists(user_name)[:limit]]

def similar_artists(artist_name, limit=3):
    artist_name = artist_name.replace(" ", "+")
    try:
        similar_artists = scrobxlib.similar(artist_name)[:limit]
    except:
        return list()
    return [artist['name'] for artist in similar_artists]

def events():
    usock = urllib.urlopen(lastfm_event_url + "1")
    soup = BeautifulSoup(usock.read())
    pages =  int(soup("a", attrs={"class":"lastpage"})[0].string)
    for page in range(1, pages+1):
        usock = urllib.urlopen(lastfm_event_url + str(page))
        soup = BeautifulSoup(usock.read())
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
            event_dict['artists'] = artists
            event_dict['venue'] = venue
            yield event_dict

if __name__ == "__main__":
    print user_top_artists("agrover", 4)
    print len(list(events()))
