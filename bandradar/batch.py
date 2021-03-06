import logging
from sqlobject.util.threadinglocal import local as threading_local
from model import (hub, BatchRecord, UserAcct, Event, Venue, Group, Recording,
                  Source, Artist, SimilarArtist, AND, OR, SQLObjectNotFound)
from sqlobject.main import SQLObjectIntegrityError
import datetime
from imports import cdbaby, amazon, lastfm, mbz
import time
import geo
import util

log = logging.getLogger("bandradar.batch")

if util.is_production():
    queries_per_run = 1000
else:
    queries_per_run = 10

artist_refresh_days = 30
venue_refresh_days = 30

def hourly_task():
    hub.threadingLocal = threading_local()
    hub.begin()
    # notify admins of pending events added by users
    events_pending = Event.select(Event.q.approved == None)
    pending_count = events_pending.count()
    unnotified = events_pending.filter(Event.q.admin_notified == False)
    if unnotified.count():
        for event in unnotified:
            event.admin_notified = True;
        for admin in Group.by_group_name("admin").users:
            util.email(admin.email_address, "BandRadar <events@bandradar.com>",
                "%d events in queue" % pending_count,
                "There are events in the pending queue.")
    hub.commit()

def nightly_task():
    log.info("batch started")
    hub.threadingLocal = threading_local()
    hub.begin()

    last = BatchRecord.select(orderBy=BatchRecord.q.last_handled).reversed()
    if last.count():
        last_rec = last[0]
        from_when = last_rec.last_handled
    else:
        from_when = datetime.date.today()

    last_handled = datetime.datetime.now()
    current = BatchRecord(first_handled=from_when, last_handled=last_handled)
    hub.commit()

    try:
        current.artists_updated = update_artists(queries_per_run)
        current.venues_updated = update_venues()
        cleanup_db()
        current.email_sent, current.artist_pings, current.venue_pings = \
            send_email(from_when, last_handled)

        current.finished = datetime.datetime.now()
        hub.commit()
    except Exception, inst:
        import traceback
        hub.rollback()
        for admin in Group.by_group_name("admin").users:
            util.email(admin.email_address, "BandRadar <events@bandradar.com>",
                "batch error", "Batch failed, Andy is on it!\n\n" + traceback.format_exc())

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
            and e.date >= CURRENT_DATE
        """ % (start, finish))
    for user_id, name, date, venue_name in results:
        evt_list = artist_email.get(user_id, list())
        evt_list.append((unicode(name, 'utf-8'), date, unicode(venue_name, 'utf-8')))
        artist_email[user_id] = evt_list
        users_to_email.add(user_id)

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
        evt_list = event_email.get(user_id, list())
        evt_list.append((unicode(event_name, 'utf-8'), venue_name))
        event_email[user_id] = evt_list
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

        for user_id, event_name, date, venue_name in results:
            venue_dict = venue_email.get(user_id, dict())
            venue = venue_dict.get(venue_name, list())
            venue.append((unicode(event_name, 'utf-8'), date))
            venue_dict[venue_name] = venue
            venue_email[user_id] = venue_dict
            users_to_email.add(user_id)

    for id in users_to_email:
        import pkg_resources

        u = UserAcct.get(id)

        event_text = ""
        for event_name, venue_name in event_email.get(id, list()):
            event_text += u"%s, at %s\n" % (event_name, venue_name)
        if event_text:
            hdr_txt = "These events you want to go to are TONIGHT!\n\n"
            event_text = hdr_txt + event_text + "\n"

        artist_text = ""
        for event_name, date, venue_name in artist_email.get(id, list()):
            artist_text += u"%s, %s at %s\n" % (event_name, date, venue_name)
        if artist_text:
            hdr_txt = "Newly added shows featuring artists you are tracking:\n\n"
            artist_text = hdr_txt + artist_text + "\n"

        venue_text = ""
        for venue_name, event_list in venue_email.get(id, dict()).iteritems():
            venue_text += venue_name + "\n" + ("-"*len(venue_name)) + "\n"
            for name, date in event_list:
                venue_text += u"%s: %s\n" % (date, name)
            venue_text += "\n"
        if venue_text:
            hdr_txt = "Upcoming shows at the venues you are tracking:\n\n"
            venue_text = hdr_txt + venue_text

        text = event_text + artist_text + venue_text

        user_url = "http://bandradar.com/users/%s" % u.user_name
        msg_to = u.email_address
        msg_from = "BandRadar Events <events@bandradar.com>"
        body = pkg_resources.resource_string(__name__, 
                    'templates/new_event_email.txt')
        body = body % {'text': text, 'user_url': user_url}

        util.email(msg_to, msg_from, "BandRadar upcoming events", body)

    return (len(users_to_email), len(artist_email), len(venue_email))

def lastfm_artist_update(artist):
    artist_info = lastfm.artist_info(artist.name)
    artist.img_url = artist_info["img_url"]
    artist.tags = artist_info['tags']
    sims_objs = []
    sims_names = artist_info["similars"]
    for artist_name in sims_names:
        try:
            sim_artist = Artist.byNameI(artist_name)
        except SQLObjectNotFound:
            # keep out too-short names
            if len(artist_name) < 3:
                continue
            try:
                sim_artist = Artist(name=artist_name, added_by=UserAcct.get(1))
            except SQLObjectIntegrityError:
                print "trying to add '%s'" % artist_name
                hub.rollback()
                hub.begin()
            # Artists added this way are *not* approved. This keeps them from
            # also having sims generated (when they could be non-local bands
            # that we really don't care much about.)
            # If they have events approved, then of course they are, too.
        sims_objs.append(sim_artist)
    artist.similars = sims_objs

def mbz_artist_update(artist):
    artist_info = mbz.artist_info(artist.name)
    while artist_info['members'] and len(artist_info['members']) > 100:
        artist_info['members'] = artist_info['members'].rsplit(",", 1)[1]
        if artist_info['members'].find(",") == -1:
            artist_info['members'] = artist_info['members'][:100]
            break
    artist.members = artist_info['members']
    artist.wikipedia_url = artist_info['wikipedia']
    artist.url = artist_info['homepage']

def recording_artist_update(artist):
    # remove old entries
    for record in Recording.selectBy(by=artist):
        record.destroySelf()

    # add new entries (if any)
    for recording in cdbaby.recordings(artist.name):
        Recording(name=recording['name'], by=artist, url=recording['url'],
            img_url=recording['img_url'], source=Source.byName("cdbaby"))
    for recording in amazon.recordings(artist.name):
        Recording(name=recording['name'], by=artist, url=recording['url'],
            img_url=recording['img_url'], source=Source.byName("amazon"))


def update_artists(count=queries_per_run):
    refresh_date = datetime.date.today() - datetime.timedelta(artist_refresh_days)
    artists = Artist.select(
        AND(Artist.q.approved != None, 
        OR(Artist.q.batch_updated == None,
           Artist.q.batch_updated < refresh_date)))
    count = min(artists.count(), count)

    email_txt = ""
    for artist in artists[:count]:
        try:
            lastfm_artist_update(artist)
            mbz_artist_update(artist)
            recording_artist_update(artist)
            artist.batch_updated = datetime.datetime.now()
        except:
            import traceback
            email_txt += "artist error: '%s'\n" % artist.name
            email_txt += traceback.format_exc()
        time.sleep(1)

    if email_txt:
        util.email("andy@bandradar.com", "BandRadar <events@bandradar.com>",
            "artist errors", email_txt)

    return count

def update_venues():
    refresh_date = datetime.date.today() - datetime.timedelta(venue_refresh_days)
    venues = Venue.select(
        AND(Venue.q.approved != None, 
        OR(Venue.q.batch_updated == None,
           Venue.q.batch_updated < refresh_date)))
    count = venues.count()
    if not util.is_production():
        count = min(count, 10)

    for venue in venues[:count]:
        if venue.zip_code:
            area = ", " + venue.zip_code
        else:
            area = ", Portland, OR"
        if venue.address:
            try:
                lat, lon, zip_code = geo.get_geocode(venue.address + area)
                venue.geocode_lat = lat
                venue.geocode_lon = lon
                if not venue.zip_code:
                    venue.zip_code = zip_code
            except IOError:
                pass
        venue.batch_updated = datetime.datetime.now()

    return count

def _foo():
    """test, do not use"""
    amazon_src = Source.byName("amazon")
    done_artists = Artist.select(Artist.q.recordings_updated != None)
    for artist in done_artists:
        for record in artist.recordings:
            if record.source == amazon_src:
                record.destroySelf()
        for recording in amazon.recordings(artist.name):
            Recording(name=recording['name'], by=artist, url=recording['url'],
                img_url=recording['img_url'], source=amazon_src)

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

