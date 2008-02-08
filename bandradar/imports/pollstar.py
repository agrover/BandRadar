from BeautifulSoup import BeautifulSoup as bs
import urllib
import datetime
import time
import re

def get_url_base():
    today = datetime.date.today()
    future = today.replace(year=today.year+1)
    url_base = "http://pollstar.com/tour/searchall.pl?By=City&Content=OR_Portland&PSKey=Y&Sort=Date&Date_From=Today&Date_To=%s&Market=N&Page="
    return url_base % future.strftime("%m-%d-%Y")

def parse_page(num):
    usock = urllib.urlopen(get_url_base()+str(num))
    soup = bs(usock.read(), convertEntities=bs.ALL_ENTITIES)
    body = soup.find('body', dict(bgcolor='#FFFFFF'))
    content = body.find('table', {'class':"content"})
    prev_tr = content.find("tr", height="20", bgcolor="00036E")
    start_tr = prev_tr.findNextSibling()
    events = {}
    for tr in start_tr.findNextSiblings():
        tds = tr.findAll("td")
        try:
            date = datetime.date(*time.strptime(tds[1].string.strip(), "%m/%d/%y")[:3])
            artist = tds[3].a.string
            venue = tds[5].a.string

            event_artists = events.get((venue, date), list())
            event_artists.append(artist)
            events[(venue, date)] = event_artists
        except IndexError:
            pass
    return events

def events():
    events = {}
    usock = urllib.urlopen(get_url_base())
    soup = bs(usock.read(), convertEntities=bs.ALL_ENTITIES)
    body = soup.find('body', dict(bgcolor='#FFFFFF'))
    contents = body.findAll('b')
    for content in contents:
        if content.string == "1":
            page_count = 1
            break
    while True:
        next = content.findNextSibling()
        if next.string in ("&gt;", ">"):
            break
        page_count += 1
        content = next
    for page in xrange(1, page_count+1):
        partial_events = parse_page(page)
        for key, artists in partial_events.iteritems():
            event_artists = events.get(key, list())
            event_artists.extend(artists)
            events[key] = event_artists

    # convert to std struct for return to import module
    venues = []
    for key, artists in events.iteritems():
        venue, date = key
        event = dict(source="pollstar")
        event['artists'] = artists
        event['date'] = date
        event['name'] = ", ".join(artists)
        event['venue'] = dict(name=venue)
        # see importers.py import_to_db() for expected layout
        yield event

if __name__ == "__main__":
    #parse_day(datetime.date.today())
    result = list(events())
    print len(result)
