import turbogears
import logging
from sqlobject.util.threadinglocal import local as threading_local
from model import (hub, BatchRecord, UserAcct, Event, Venue,
                  Artist, SimilarArtist, AND, SQLObjectNotFound)
import datetime
from imports import lastfm
import time
from imports import google

log = logging.getLogger("bandradar.batch")

def task():
    log.info("batch started")
    hub.threadingLocal = threading_local()
    hub.begin()

    last = BatchRecord.select(orderBy=BatchRecord.q.last_handled).reversed()[:1]
    if last.count():
        last_rec = last[0]
        from_when = last_rec.last_handled
    else:
        from_when = datetime.date.today()

    last_handled = datetime.datetime.now()
    current = BatchRecord(first_handled=from_when, last_handled=last_handled)
    hub.commit()

    try:
        current.email_sent, current.artist_pings, current.venue_pings = \
            send_email(from_when, last_handled)
        current.sims_updated = build_similars()
        current.geocodes_updated = build_geocodes()
        cleanup_db()

        current.finished = datetime.datetime.now()
        hub.commit()

    finally:
        log.info("batch finished")
        hub.end()

def send_email(start, finish):
    conn = hub.getConnection()

    users_to_email = set()

    #
    # Gather results for tracked artists. Notify if events added since last update
    #
    artist_email = {}
    results = conn.queryAll("""
        select u.id, e.name, e.date, v.name
        from user_acct u, artist_user_acct au, artist a, artist_event ae, event e, venue v
        where
            u.event_email is true
            and u.id = au.user_acct_id
            and a.id = au.artist_id
            and a.id = ae.artist_id
            and ae.event_id = e.id
            and e.venue_id = v.id
            and e.created >= '%s'
            and e.created < '%s'
        """ % (start, finish))
    for id, name, date, venue_name in results:
        evt_list = artist_email.get(id, list())
        evt_list.append((name, date, venue_name))
        artist_email[id] = evt_list
        users_to_email.add(id)

    #
    # Gather results for tracked events. Notify if they're today
    #
    event_email = {}
    results = conn.queryAll("""
        select e.id, e.name, att.user_id, v.name
        from event e, attendance att, venue v
            where e.date = CURRENT_DATE
            and e.id = att.event_id
            and e.venue_id = v.id
        """)
    for event_id, event_name, user_id, venue_name in results:
        evt_list = event_email.get(id, list())
        evt_list.append((event_name, venue_name))
        artist_email[id] = evt_list
        users_to_email.add(user_id)

    # Gather results for tracked venues. Once a week.
    # why do this here, instead of having a separate scheduled function called?
    # because we want to put both artist and venue notifications in the same email.
    venue_email = {}
    if finish.isoweekday() == 4:
        results = conn.queryAll("""
            select u.id, e.name, e.date, v.name
            from user_acct u, venue v, event e, user_acct_venue uv
            where
                u.event_email is true
                and e.venue_id = v.id
                and u.id = uv.user_acct_id
                and uv.venue_id = v.id
                and e.date >= CURRENT_DATE
                order by e.date
            """)

        for id, event_name, date, venue_name in results:
            venue_dict = venue_email.get(id, dict())
            venue = venue_dict.get(venue_name, list())
            venue.append((event_name, date))
            venue_dict[venue_name] = venue
            venue_email[id] = venue_dict
            users_to_email.add(id)

    for id in users_to_email:
        import smtplib
        import pkg_resources
        from email.MIMEText import MIMEText
        from email.Utils import make_msgid

        u = UserAcct.get(id)

        event_text = ""
        for event_name, venue_name in event_email.get(id, list()):
            event_text += "%s, at %s\n" % (event_name, venue_name)
        if event_text:
            hdr_txt = "These events you want to go to are TONIGHT!\n\n"
            event_text = hdr_txt + event_text + "\n"

        artist_text = ""
        for event_name, date, venue_name in artist_email.get(id, list()):
            artist_text += "%s, %s at %s\n" % (event_name, date, venue_name)
        if artist_text:
            hdr_txt = "Newly added shows featuring artists you are tracking:\n\n"
            artist_text = hdr_txt + artist_text + "\n"

        venue_text = ""
        for venue_name, event_list in venue_email.get(id, dict()).iteritems():
            venue_text += venue_name + "\n" + ("-"*len(venue_name)) + "\n"
            for name, date in event_list:
                venue_text += "%s: %s\n" % (date, name)
        if venue_text:
            hdr_txt = "Upcoming shows at the venues you are tracking:\n\n"
            venue_text = hdr_txt + venue_text + "\n"

        text = event_text + artist_text + venue_text

        user_url = "http://bandradar.com/users/%s" % u.user_name

        msg_to = u.email_address
        msg_from = "BandRadar Events <events@bandradar.com>"
        body = pkg_resources.resource_string(__name__, 
                    'templates/new_event_email.txt')
        body  = body % {'text': text, 'user_url': user_url}
        msg = MIMEText(body)
        msg['Subject'] = "BandRadar upcoming events"
        msg['From'] = msg_from
        msg['To'] = msg_to
        msg['Message-ID'] = make_msgid()

        s = smtplib.SMTP()
        s.connect()
        try:
            s.sendmail(msg_from, [msg_to], msg.as_string())
        except smtplib.SMTPException, smtp:
            # todo: record bounces so a human can do something
            log.error("smtp error %s" % repr(smtp))
        s.close()

    return (len(users_to_email), len(artist_email), len(venue_email))

def build_similars(count=3600):
    admin = UserAcct.get(1)
    # Do 3600 artists at a time, only hitting last.fm for an hour...
    artists = Artist.select(
        AND(Artist.q.approved != None, Artist.q.sims_updated == None))[:count]
    artist_num = artists.count()
    for artist in artists:
        sims_objs = []
        sims_names = lastfm.similar_artists(artist.name)
        for artist_name in sims_names:
            try:
                sim_artist = Artist.byNameI(artist_name)
            except SQLObjectNotFound:
                sim_artist = Artist(name=artist_name, added_by=admin)
                # Artists added this way are *not* approved. This keeps them from
                # also having sims generated (when they could be non-local bands
                # that we really don't care much about.)
                # If they have events approved, then of course they are, too.
            sims_objs.append(sim_artist)
        artist.similars = sims_objs
        artist.sims_updated = datetime.datetime.now()
        time.sleep(1)
    return artist_num

def build_geocodes():
    venues = Venue.selectBy(geocode_lat=None)
    for venue in venues:
        if venue.zip_code:
            area = ", " + venue.zip_code
        else:
            area = ", Portland, OR"
        if venue.address:
            try:
                lat, lon = google.get_geocode(venue.address + area)
                venue.geocode_lat = lat
                venue.geocode_lon = lon
            except IOError:
                pass
    return venues.count()

def cleanup_db():
    from model import VisitIdentity
    from turbogears.visit.sovisit import TG_Visit

    now = datetime.datetime.now()
    old_visits = TG_Visit.select(TG_Visit.q.expiry < now)
    for old_visit in old_visits:
        try:
            visit_identity = VisitIdentity.by_visit_key(old_visit.visit_key)
            if visit_identity.expiry == None or visit_identity.expiry < now:
                visit_identity.destroySelf()
        except SQLObjectNotFound:
            pass
        old_visit.destroySelf()

