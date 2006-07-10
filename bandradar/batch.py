import turbogears
import logging
from sqlobject.util.threadinglocal import local as threading_local
from model import hub, BatchRecord, Event
import datetime

log = logging.getLogger("bandradar.batch")

def task():
    log.info("batch started")
    hub.threadingLocal = threading_local()
    hub.begin()
    last = BatchRecord.select(orderBy=BatchRecord.q.last_handled).reversed()[:1]
    if len(list(last)):
        last_rec = last[0]
        from_when = last_rec.last_handled
    else:
        from_when = datetime.date.today()

    current = BatchRecord(first_handled=from_when, last_handled=datetime.datetime.now())
    hub.commit()

    send_to = {}
    new_events = Event.select(Event.q.created > from_when)
    for event in new_events:
        for artist in event.artists:
            for user in artist.users:
                user_events = send_to.get(user, set())
                user_events.add(event)
                send_to[user] = user_events

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
        except smtplib.SMTPException, smtp:
            # todo: record bounces so a human can do something
            log.error("smtp error %s" % repr(smtp))
        s.close()

    current.finished = datetime.datetime.now()
    hub.commit()
    hub.end()
    log.info("batch finished")
