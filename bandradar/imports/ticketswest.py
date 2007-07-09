from BeautifulSoup import BeautifulSoup
import urllib
import datetime
import time
import re

venue_list = (("Doug Fir", "DFL"), ("Roseland", "ROS"),
               ("Berbati's Pan", "BER"), ("Dante's", "DAN"),
               ("Hawthorne Theatre", "HAW"), ("Fez Ballroom", "FEZ"))

base_url = "http://ticketswest.rdln.com"
page_url = "/Venue.aspx?ven="

def events(venues=venue_list):
    for venue_name, code in venues:
        usock = urllib.urlopen(base_url + page_url + code)
        soup = BeautifulSoup(usock.read())
        try:
            table = soup("table", attrs={"class":"eventDataGrid"})[0]
        except IndexError:
            continue
        trs = table("tr")[1:-1]
        venue = dict(name=venue_name)
        for tr in trs:
            event = dict(source="ticketswest")
            name_td = tr("td", attrs={"class":"borderTopRight paddedLeft"})[0]
            name = name_td.a.string
            match = re.compile(r' [Aa][Tt] ').search(name)
            if match:
                name = name[:match.start()]
            event['artists'] = name.split("*")[0].split(",")
            event['artists'] = [a.strip() for a in event['artists']]
            event['name'] = ", ".join(event['artists'])
            date_td = tr("td", attrs={"class":"borderTopRight"})[0]
            if not date_td.string:
                continue
            weekday, date_str, time_str, ampm =  date_td.string.strip().split()
            event['date'] = datetime.date(*time.strptime(date_str, "%m/%d/%y")[:3])
            if time_str.endswith(":00"):
                time_str = time_str.split(":")[0]
            event['time'] = time_str + " " + ampm
            link_td = tr("td")[3]
            event['ticket_url'] =  base_url + link_td.div.a.attrs[1][1]
            event['venue'] = venue
            yield event

if __name__ == "__main__":
    results = list(events(venues=[("Roseland", "ROS")]))
    for result in results:
        print result['name']
    print len(results)
