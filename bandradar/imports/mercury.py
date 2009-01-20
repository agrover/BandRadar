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
    baseurl = "http://www.portlandmercury.com/gyrobase/EventSearch?eventCategory=807942&eventSection=807941&narrowByDate="
    return baseurl + date.strftime("%Y-%m-%d")

def event_urls_for_date(date):
    page = 1
    while True:
        soup = import_util.url_to_soup(date_to_url(date) + "&page=%s" % page)
        events = soup.findAll("div", "EventListing clearfix")
        if not len(events):
            break
        for event in events:
            yield event.div.h3.find("a", recursive=False)['href']
        page += 1

def day_events(date):
    for url in event_urls_for_date(date):
        soup = import_util.url_to_soup(url)
        event = dict(source="mercury")
        event['date'] = date

        lt = soup.find("h1", "listingTitle")
        crap = lt.find("div", "FeaturesIcons")
        if crap:
            crap.extract()
        event['name'] = import_util.stringify(lt).strip()

        el = soup.find("div", id="EventLocation")
        event['venue'] = dict(name=el.ul.li.h4.find("a", recursive=False).string)
        event['artists'] = []

        artists_str = event['name']
        if artists_str.find(":") != -1:
            event['name'], artists_str = artists_str.split(":", 1)
        event['artists'] = artists_str.split(",")
        event['artists'] = [a.strip() for a in event['artists']]
        yield event

def week_events(start_date):
    for i in range(7):
        for event in day_events(start_date + datetime.timedelta(i)):
            yield event

if __name__ == "__main__":
    for event in day_events(datetime.date.today()):
        print "Venue: " + event['venue']['name']
        print "  " + event.get("name", "no event name")
        for artist in event['artists']:
            print "    artist: " + artist

