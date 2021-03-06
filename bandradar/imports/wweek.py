import datetime
import dateutil.relativedelta as drd
import time
import re
import import_util

def date_to_url(date):
    baseurl = "http://localcut.wweek.com/calendar/"
    datestr = date.strftime("%A/").lower()
    return baseurl + datestr

def parse_event(event):
    event_name = ""
    p = re.compile(r"\([\w\s:]*?[ap]m\)")
    event = p.sub("", event)
    # find name (if present)
    if event.rfind(':') != -1:
        event_name, event = event.split(':', 1)
    elif event.rfind('w/') != -1:
        event_name, event = event.split('w/', 1)

    p = re.compile("[,;]")
    artists = p.split(event)
    artists = [a.strip(' "\n') for a in artists]
    artists = [a.replace(" & friends", "") for a in artists]
    artists = [a.replace(" & guests", "") for a in artists]
    if artists[0].startswith("DJs"):
        artists[0] = artists[0].replace("DJs", "")
        artists = ["DJ " + a.strip() for a in artists]
    if not event_name:
        event_name = ", ".join(artists)
    return event_name, artists

def day_events(date):
    soup = import_util.url_to_soup(date_to_url(date))
    #find all anchors with e.g. name="42820"
    anchors = soup('a', {'name':re.compile("\d+")})
    for anchor in anchors:
        small = anchor.findNextSibling("small")
        event = dict(date=date, source="wweek")
        venue_stuff = small.contents[1].strip("| ")
        address, phone = venue_stuff.rsplit(",", 1)
        event['venue'] = dict(name=small.b.string, address=address, phone=phone)
        event_name_span = small.findNextSibling("span", "headout_event")
        event_name = import_util.stringify(event_name_span)
        if len(event_name) < 2:
            continue
        event['name'], event['artists'] = parse_event(event_name)
        yield event

def week_events():
    # start last Wednesday
    start_date = datetime.date.today()+drd.relativedelta(weekday=drd.WE(-1))
    for i in range(7):
        for event in day_events(start_date + datetime.timedelta(i)):
            yield event

if __name__ == "__main__":
    #print len(list(day_events(datetime.date.today()+datetime.timedelta(2))))
    #print len(list(day_events(datetime.date.today())))
    #print len(list(day_events(datetime.date(2008, 2, 16))))
    print len(list(week_events()))

