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

def events():
    for venue_name, code in venue_list:
        usock = urllib.urlopen(base_url + page_url + code)
        soup = BeautifulSoup(usock.read())
        table = soup("table", attrs={"class":"eventDataGrid"})[0]
        trs = table("tr")[1:-1]
        venue = dict(name=venue_name)
        for tr in trs:
            event = dict(source="ticketswest")
            name_td = tr("td", attrs={"class":"borderTopRight paddedLeft"})[0]
            event['artists'] = name_td.a.string.split("*")[0].split(",")
            event['name'] = ", ".join(event['artists'])
            date_td = tr("td", attrs={"class":"borderTopRight"})[0]
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
    result = list(events())
    print len(result)
