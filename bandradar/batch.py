import turbogears
import logging
from sqlobject.util.threadinglocal import local as threading_local
from model import (hub, BatchRecord, UserAcct, Event,
                  Artist, SimilarArtist, AND, SQLObjectNotFound)
import datetime
import lastfm
import time

log = logging.getLogger("bandradar.batch")

def task():
    log.info("batch started")
    hub.threadingLocal = threading_local()
    hub.begin()

    try:
        send_email()
        build_similars()
        cleanup_db()

    finally:
        log.info("batch finished")
        hub.end()

def send_email():

    last = BatchRecord.select(orderBy=BatchRecord.q.last_handled).reversed()[:1]
    if len(list(last)):
        last_rec = last[0]
        from_when = last_rec.last_handled
    else:
        from_when = datetime.date.today()

    last_handled = datetime.datetime.now()
    current = BatchRecord(first_handled=from_when, last_handled=last_handled)
    hub.commit()

    send_to = {}
    # date range includes start, doesn't include end instant
    # (next iteration will handle) 
    new_events = Event.select(AND(Event.q.approved >= from_when,
        Event.q.approved < last_handled, Event.q.date > datetime.date.today()))
    for event in new_events:
        for artist in event.artists:
            for user in artist.users:
                if user.event_email:
                    user_events = send_to.get(user, set())
                    user_events.add(event)
                    send_to[user] = user_events

    email_sent = 0
    for u, events in send_to.iteritems():
        import smtplib
        import pkg_resources
        from email.MIMEText import MIMEText

        event_list = []
        for event in events:
            event_str = "%s, %s at %s" % (event.name, event.date, event.venue.name)
            event_list.append(event_str)
        event_info = "\n".join(event_list)
        user_url = "http://bandradar.com/users/%s" % u.user_name

        msg_to = u.email_address
        msg_from = "BandRadar Events <events@bandradar.com>"
        body = pkg_resources.resource_string(__name__, 
                    'templates/new_event_email.txt')
        body  = body % {'event_info': event_info, 'user_url': user_url}
        msg = MIMEText(body)
        msg['Subject'] = "BandRadar upcoming events"
        msg['From'] = msg_from
        msg['To'] = msg_to

        s = smtplib.SMTP()
        s.connect()
        try:
            s.sendmail(msg_from, [msg_to], msg.as_string())
            email_sent += 1
        except smtplib.SMTPException, smtp:
            # todo: record bounces so a human can do something
            log.error("smtp error %s" % repr(smtp))
        s.close()

    current.email_sent = email_sent;
    current.finished = datetime.datetime.now()
    hub.commit()

def build_similars():
    admin = UserAcct.get(1)
    # Do 100 artists at a time
    artists = Artist.select(
        AND(Event.q.approved != None, Artist.q.sims_updated == None))[:100]
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
                # that we really don't care much about.
                # If they have events approved, then of course they are, too.
            sims_objs.append(sim_artist)
        artist.similars = sims_objs
        artist.sims_updated = datetime.datetime.now()
        time.sleep(1)
    hub.commit()

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
    hub.commit()
