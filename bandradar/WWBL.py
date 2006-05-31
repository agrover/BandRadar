from BeautifulSoup import BeautifulSoup
import urllib
import datetime
import time
import re

# venues = [venue]
# venue = {name, addr, phone, [events]}
# events = {name, [artists], date(date), str(time), str(cost)}
# artists = [artist]

class WWBL:

    def parse_event(self, event):
        event_name = ""
        # find name (if present)
        if event.rfind(':') != -1:
            event_name, event = event.split(':', 1)
        elif event.rfind('w/') != -1:
            event_name, event = event.split('w/')

        artists = [a.strip(' "') for a in event.split(",")]
        if not event_name:
            event_name = ", ".join(artists)
        return event_name, artists

    def u(self, string):
        return unicode(string, 'latin1')

    def parse_day(self, date):
        venues = []
        baseurl = "http://wweek.com/calendar/music/index.php?date="
        datestr = str(int(time.mktime(date.timetuple())))
        url = baseurl + datestr
        usock = urllib.urlopen(url)
        soup = BeautifulSoup(usock.read())
        #find all anchors with e.g. name="42820"
        anchors = soup('a', {'name':re.compile("\d+")})
        for anchor in anchors:
            venue = {}
            venue['events'] = []

            if anchor.parent.name == "div":
                # handle wweek "preview" entries
                event_dict = {}
                div = anchor.parent
                event_dict['name'], event_dict['artists'] = \
                    self.parse_event(self.u(div.h2.string.strip()))
                venue["name"] = self.u(anchor.findNextSibling('b').string.strip())
                txt = div.fetchText(re.compile("\|.*"), recursive=False)
                result = txt[0].replace("[|", " ").strip().split(",")
                venue["addr"] = result[0].strip()
                venue["phone"] = result[1].strip()
                # get italicized text
                ielems = div.fetch('i')
                for i in ielems:
                    if i.string:
                        event_dict['time'], event_dict['cost'], event_dict['ages'] = \
                            self.parse_preview_moreinfo(i.string)
                event_dict['date'] = date
                venue['events'].append(event_dict)
            elif anchor.parent.name == "p":
                # handle normal entries
                p = anchor.parent
                txt = p.fetchText(re.compile("\|.*"), recursive=False)
                cleantxt = txt[0].strip().strip('[|').strip()
                addr_phone = [txt.strip() for txt in cleantxt.split(",")]
                if len(addr_phone) > 0:
                    venue['addr'] = addr_phone[0]
                    if len(addr_phone) > 1:
                        venue['phone'] = addr_phone[1] 
                b1 = p.findNext('b')
                venue['name'] = self.u(b1.string.strip())
                b2 = b1.findNext('b')
                events = b2.string.strip().split(";")
                for event in events:
                    event_dict = {}
                    m = re.search(r'(.*?)\(([\d:&]+\ ?[ap]m)\)$', event)
                    if m:
                        event_dict['time'] = m.group(2)
                        event = self.u(m.group(1))
                    event_dict['name'], event_dict['artists'] = self.parse_event(event)
                    event_dict['date'] = date
                    venue['events'].append(event_dict)
        
            venues.append(venue)
        return venues

    def parse_preview_moreinfo(self, text):
        #moreinfo = text.split(".", 1)[1].strip()
        m = re.search(r'([\d:&]+\ ?[ap]m)\.?(.*?)\.(.*?)\.', text)
        if not m:
            return ("UNK", "UNK", "UNK")
        time = m.group(1)
        cost = m.group(2).strip()
        ages = m.group(3).strip()
        return (time, cost, ages)

    def parse_week(self, start_date):
        venues = []
        for i in range(7):
            venues.extend(self.parse_day(start_date + datetime.timedelta(i)))
        return venues

if __name__ == "__main__":
    wwbl = WWBL()
    wwbl.parse_day(datetime.date.today())
    #wwbl.parse_day(datetime.date(2006, 4, 22))

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
