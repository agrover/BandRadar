
import upcoming
from datetime import date

local_metro_ids = upcoming.config.get("local","metros").split()

api = upcoming.api()

def clean(string):
    temp = string.strip().replace("&amp;", "&")
    return " ".join(temp.split())

def events():
    for metro_id in local_metro_ids:
        metro = api.metro.getInfo(metro_id=metro_id)[0]
        # get music events
        events = metro.events(category_id=1)
        for event in events:
            if not (int(event.personal)):
                event_date = date(*[int(num) for num in event.start_date.split('-')])
                event_time = None
                if event.start_time:
                    hrs, mins = [int(num) for num in event.start_time.split(':')[:2]]
                    suff = "am"
                    if hrs > 12:
                        hrs -= 12
                        suff = "pm"
                    event_time = unicode(hrs)
                    if mins:
                        event_time += ":" + unicode(mins)
                    event_time += " " + suff
                event_description = event.description
                try:
                    ev = api.venue.getInfo(venue_id=int(event.venue_id))[0]
                except IndexError:
                    continue
                venue = dict(name=ev.name, url=ev.url, zip_code=ev.zip, address=ev.address,
                             phone=ev.phone, description=ev.description)
                # see importers.py import_to_db() for expected layout
                yield dict(name=clean(event.name), date=event_date, time=event_time,
                           description=clean(event.description),
                           artists=clean(event.name).split(','),
                           venue=venue)

if __name__ == "__main__":
    for event in events():
        print event['name'], event['time']

