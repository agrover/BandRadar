from BeautifulSoup import BeautifulSoup
import urllib
import datetime
import time
import re

def artist_clean(artist):
    artist = artist.replace("(taverna)", "")
    return " ".join.artist.split()

def date_to_url(date):
    baseurl = "http://wweek.com/calendar/music/index.php?date="
    datestr = str(int(time.mktime(date.timetuple())))
    return baseurl + datestr

def parse_event(event):
    event_name = ""
    # find name (if present)
    if event.rfind(':') != -1:
        event_name, event = event.split(':', 1)
    elif event.rfind('w/') != -1:
        event_name, event = event.split('w/', 1)

    artists = [a.strip(' "') for a in event.split(",")]
    artists = [a.replace(" & friends", "") for a in artists]
    artists = [a.replace(" & guests", "") for a in artists]
    if artists[0].startswith("DJs"):
        artists[0] = artists[0].replace("DJs", "")
        artists = ["DJ " + a.strip() for a in artists]
    if not event_name:
        event_name = ", ".join(artists)
    return event_name, artists

def parse_preview_moreinfo(text):
    m = re.search(r'([\d:&]+\ ?[ap]m)\.? (.*?)\. (.*?)\.', text)
    if not m:
        return (None, None, None)
    time = m.group(1)
    cost = m.group(2).strip()
    ages = m.group(3).strip()
    return (time, cost, ages)

def day_events(date):
    usock = urllib.urlopen(date_to_url(date))
    soup = BeautifulSoup(usock.read(), fromEncoding="mac-roman")
    #find all anchors with e.g. name="42820"
    anchors = soup('a', {'name':re.compile("\d+")})
    for anchor in anchors:
        if anchor.parent.name == "div":
            # handle wweek "preview" entries
            venue = {}
            event_dict = {}
            div = anchor.parent
            event_dict['name'], event_dict['artists'] = \
                parse_event(div.h2.string.strip())
            venue["name"] = anchor.findNextSibling('b').string.strip()
            txt = div.findAll(text=re.compile("\|.*"), recursive=False)
            result = txt[0].strip().split(",", 1)
            venue["address"] = result[0].strip()
            venue["phone"] = result[1].split(",")[0].strip(" [|")
            # get italicized text
            ielems = div.findAll('i')
            for i in ielems:
                if i.string:
                    event_dict['time'], event_dict['cost'], event_dict['ages'] = \
                        parse_preview_moreinfo(i.string)
            event_dict['date'] = date
            event_dict['venue'] = venue
            # see importers.py import_to_db() for expected layout
            yield event_dict
        elif anchor.parent.name == "p":
            # handle normal entries
            venue = {}
            p = anchor.parent
            txt = p.findAll(text=re.compile("\|.*"), recursive=False)
            cleantxt = txt[0].strip().strip('[|').strip()
            addr_phone = [txt.strip() for txt in cleantxt.split(",")]
            if len(addr_phone) > 0:
                venue['address'] = addr_phone[0]
                if len(addr_phone) > 1:
                    venue['phone'] = addr_phone[1] 
            b1 = p.findNext('b')
            if not b1.string:
                continue
            venue['name'] = b1.string.strip()
            b2 = b1.findNext('b')
            if not b2.string:
                continue
            events = b2.string.strip().split(";")
            for event in events:
                event_dict = {}
                event_dict['venue'] = venue
                m = re.search(r'(.*?)\(([\d:&]+\ ?[ap]m)\)$', event)
                if m:
                    event_dict['time'] = m.group(2)
                    event = m.group(1)
                event_dict['name'], event_dict['artists'] = parse_event(event)
                event_dict['date'] = date
                yield event_dict

def week_events(start_date):
    for i in range(7):
        for event in day_events(start_date + datetime.timedelta(i)):
            yield event

def month_events(start_date):
    end_date = start_date.replace(month=start_date.month+1)
    end_date = end_date - datetime.timedelta(1)
    for i in xrange(end_date.day):
        for event in day_events(start_date + datetime.timedelta(i)):
            yield event

if __name__ == "__main__":
    #parse_day(datetime.date.today())
    print len(list(day_events(datetime.date(2007, 2, 22))))

#find named anchors
# if a.parent = div class preview
# 1st b = artists name
# 1st h2 = event name
# 1st i = venue name, time, cost, ages
#else if a.parent = p
# 1st b = venue name
# 2nd b = artists, separated by ;, with times in ()
#   double shows separated by & in ()
# address & phone = p text minus symbols
