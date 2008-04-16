#
# Mercury importer
#

import datetime
import time
import re
import import_util
import logging

log = logging.getLogger("bandradar.controllers")

def date_to_url(date):
    baseurl = "http://www.portlandmercury.com/portland/FoundIt?search=music&musicBand1=&musicBand2=&musicCategory=&musicLocation=&musicStartDate="
    return baseurl + date.strftime("%Y-%m-%d")

def day_events(date):
    soup = import_util.url_to_soup(date_to_url(date))
    events = soup.findAll("div", "event_group ")
    events.extend(soup.findAll("div", "event_group staffpick_music"))
    for event_div in events:
        event = dict(source="mercury")
        event['date'] = date
        event['venue'] = dict(name=event_div.h4.a.string)
        event['artists'] = []
        for li in event_div.find("ul", "event_musicians").findAll("li"):
            artist_name = "".join([x.string for x in li.contents if x.string]).strip()
            event['artists'].append(artist_name)
        if not len(event['artists']):
            continue
        if event_div.h5:
            event['name'] = import_util.stringify(event_div.h5).strip(":")
        else:
            event['name'] = ", ".join(event['artists'])
        if event_div.p.strong:
            event['cost'] = event_div.p.strong.string
        yield event

def week_events(start_date):
    for i in range(7):
        for event in day_events(start_date + datetime.timedelta(i)):
            yield event

if __name__ == "__main__":
    for event in day_events(datetime.date.today() - datetime.timedelta(1)):
        print "Venue: " + event['venue']['name']
        print "  " + event.get("name", "no event name")
        for artist in event['artists']:
            print "    artist: " + artist

