from BeautifulSoup import BeautifulSoup
import urllib
import datetime
import time
import re

# venues = [venue]
# venue = {name, addr, phone, [events]}
# events = {name, [artists], date(date), str(time), str(cost)}
# artists = [artist]

def get_url_base():
    today = datetime.date.today()
    future = today.replace(year=today.year+1)
    url_base = "http://pollstar.com/tour/searchall.pl?By=City&Content=OR_Portland&PSKey=Y&Sort=Date&Date_From=Today&Date_To=%s&Market=N&Page="
    return url_base % future.strftime("%m-%d-%Y")

def clean(string):
    temp = string.strip().replace("&amp;", "&")
    return " ".join(temp.split())

def parse_page(num):
    usock = urllib.urlopen(get_url_base()+str(num))
    soup = BeautifulSoup(usock.read(), convertEntities=BeautifulSoup.HTML_ENTITIES)
    body = soup.find('body', dict(bgcolor='#FFFFFF'))
    content = body.find('table', {'class':"content"})
    prev_tr = content.find("tr", height="20", bgcolor="00036E")
    start_tr = prev_tr.findNextSibling()
    events = {}
    for tr in start_tr.findNextSiblings():
        tds = tr.findAll("td")
        try:
            date = datetime.date(*time.strptime(clean(tds[1].string), "%m/%d/%y")[:3])
            artist = clean(tds[3].a.string)
            venue = clean(tds[5].a.string)

            event_artists = events.get((venue, date), list())
            event_artists.append(artist)
            events[(venue, date)] = event_artists
        except IndexError:
            pass
    return events

def parse_all():
    events = {}
    usock = urllib.urlopen(get_url_base())
    soup = BeautifulSoup(usock.read())
    body = soup.find('body', dict(bgcolor='#FFFFFF'))
    contents = body.findAll('b')
    for content in contents:
        if content.string == "1":
            page_count = 1
            break
    while True:
        next = content.findNextSibling()
        if next.string == "&gt;":
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
        event = {}
        event['artists'] = artists
        event['date'] = date
        event['name'] = ", ".join(artists)
        venues.append(dict(name=venue, events=[event]))

    return venues

if __name__ == "__main__":
    #parse_day(datetime.date.today())
    result = parse_all()
    print len(result)
