from sgmllib import SGMLParser
import urllib
import datetime
import re

# venues = [venue]
# venue = {name, addr, phone, [events]}
# events = {name, [artists], date(date), str(time), str(cost)}
# artists = [artist]


class MercuryBandParser(SGMLParser):

    def reset(self):
        SGMLParser.reset(self)
        self.venues = []
        self.current_event = ""
        self.event_date = None
        self.div_cnt = 0
        self.p_cnt = 0
        self.h2_cnt = 0

    def venue_parse(self, current_event, event_date):
        if len(current_event) < 5:
            return
        match = re.compile(r'(.*?)-(.*)').match(current_event)
        venue_name = match.group(1).strip()
        venue_name = venue_name.replace("&", " & ")
        venue = {}
        venue["name"] = venue_name
        venue["events"] = []
        # multiple events at same venue delimited by ";"
        shows = match.group(2).split(";")
        for show in shows:

            show_dict = {}
            show_dict["name"] = []
            show_dict["artists"] = []

            # find the cost
            match = re.compile(r'(.*?)((free|\$[\d-]+)(.*))?$').match(show)
            appearing = match.group(1).strip(' ,')
            cost = match.group(3) or ""

            # find the time
            match = re.compile(r'(.*?)([\d:&]+\ ?[ap]m)?$').match(appearing)
            appearing = match.group(1)
            time = match.group(2) or ""

            artists = []
            # get event name
            event_name = ""
            if appearing.rfind(':') != -1:
                event_name, appearing = appearing.split(':', 1)
            elif appearing.rfind('w/') != -1:
                event_name, appearing = appearing.split('w/')
            event_name = event_name.replace("&", " & ")
            event_name = event_name.strip()

            def artist_clean(artist):
                artist = artist.strip()
                artist = artist.replace("&", " & ", 1)
                # elim. (xx) from "blah (xx)"
                match = re.compile(r'^(.*?)(\(\w+\))?$').match(artist)
                if match.group(2):
                    artist = match.group(1).strip()
                return artist

            # get artists
            artists = appearing.strip(' ,').split(',')
            artists = [artist_clean(artist) for artist in artists]

            if not event_name:
                event_name = ", ".join(artists)

            # put it all in a dict
            if cost: show_dict["cost"] = cost
            if time: show_dict["time"] = time
            if event_name: show_dict["name"] = event_name
            if artists: show_dict["artists"] = artists
            show_dict["date"] = event_date

            venue["events"].append(show_dict)

        return venue

    def start_div(self, attrs):
        id = [v for (k, v) in attrs if k=='id']
        if self.div_cnt:
            self.div_cnt += 1
            
        if id and not self.div_cnt:
            if id[0] == "listings":
                self.div_cnt = 1

    def end_div(self):
        if self.div_cnt:
            self.div_cnt -= 1

    def start_p(self, attrs):
        if self.div_cnt:
            self.current_event = ""
            self.p_cnt += 1

    def end_p(self):
        if self.p_cnt == 1 and self.div_cnt == 1 and self.current_event:
            venues = self.venue_parse(self.current_event, self.event_date)
            if venues:
                self.venues.append(venues)
        self.p_cnt -= 1

    def start_h2(self, attrs):
        if self.div_cnt == 1:
            self.h2_cnt = 1

    def end_h2(self):
        self.h2_cnt = 0

    def handle_data(self, data):
        data = data.strip()
        if self.div_cnt:
            # set event_date if in an <h2>
            if self.h2_cnt:
                match = re.compile(r'\w+\s+(\d+)\/(\d+)').search(data)
                date = datetime.date.today()
                self.event_date = date.replace(month=int(match.group(1)), \
                    day=int(match.group(2)))
            # else it's a event (possibly partial) so remember it
            elif len(data) and not data.startswith("MEANS WE RECOMMEND IT") \
                and not data.startswith("DJ LISTINGS"):
                self.current_event += data
            
def parse_week(url):
    usock = urllib.urlopen(url)
    parser = MercuryBandParser()
    parser.feed(usock.read())
    usock.close()
    return parser.venues

if __name__ == "__main__":
    usock = urllib.urlopen("http://www.portlandmercury.com/portland/Content?oid=37590&category=22185")
    parser = MercuryBandParser()
    parser.feed(usock.read())
    usock.close()
    for venue in parser.venues:
        print venue
