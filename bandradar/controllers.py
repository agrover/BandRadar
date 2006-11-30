import logging
import cherrypy
import turbogears
from turbogears import controllers, expose, redirect
from turbogears import identity
from turbogears import scheduler
from turbogears import widgets as w
from turbogears import validators as v
from sqlobject import AND

from artists import Artists, artist_search_form
from venues import Venues
from events import Events
from users import Users
from importers import Importers
from comments import Comments
from model import Event, Comment, hub
import batch
import saved_visit
import util

import datetime

log = logging.getLogger("bandradar.controllers")


def br_startup():
    #scheduler.add_interval_task(batch.task, 60)
    scheduler.add_weekday_task(batch.task, range(1,8), (3,0))
    saved_visit.start_extension()

def br_shutdown():
    saved_visit.shutdown_extension()

turbogears.startup.call_on_startup.append(br_startup)
turbogears.startup.call_on_shutdown.append(br_shutdown)


class Root(controllers.RootController):

    @expose(template=".templates.main")
    def index(self):
        if identity.current.user:
            user = identity.current.user.user_name
        else:
            user = "unknown person"

        events = Event.select(AND(Event.q.date == datetime.date.today(),
            Event.q.approved != None),
            orderBy=Event.q.name)#[:10]

        conn = hub.getConnection()
        top_tracked_results = conn.queryAll("""
            select artist.name, artist.id, COUNT(artist_user_acct.user_acct_id) as count
            from artist
            left join artist_user_acct on artist.id = artist_user_acct.artist_id
            group by artist.name, artist.id
            order by count desc, name
            limit 20
            """)

        top_tracked = []
        for name, id, count in top_tracked_results:
            top_tracked.append(dict(name=name, id=id, count=count))

        return dict(user=user, search_form=artist_search_form, events=events,
            top_tracked=top_tracked)

    artists = Artists()
    venues = Venues()
    events = Events()
    users = Users()
    importers = Importers()
    comments = Comments()

    @expose(template=".templates.output")
    def test(self):
        return dict(output="hello")
        #return dict(output=str(identity.current_provider))

    @expose(template=".templates.about")
    def about(self):
        return dict()

    @expose(template=".templates.privacy")
    def privacy(self):
        return dict()

    @expose(template=".templates.notimplemented")
    def contact(self):
        return dict()

    @expose(template=".templates.notimplemented")
    def feeds(self):
        return dict()
