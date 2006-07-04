import logging
import cherrypy
import turbogears
from turbogears import controllers, expose, redirect
from turbogears import identity

from artists import Artists, artist_search_form
from venues import Venues
from events import Events
from users import Users
from importers import Importers
from model import Event

import datetime

log = logging.getLogger("bandradar.controllers")

def br_startup():
    log.info("BandRadar started")

turbogears.startup.call_on_startup.append(br_startup)


class Root(controllers.RootController):

    @expose(template=".templates.main")
    def index(self):
        log.debug("Happy TurboGears Controller Responding For Duty")
        if identity.current.user:
            user = identity.current.user.user_name
        else:
            user = "unknown person"

        events = Event.select(Event.q.date == datetime.date.today(),
            orderBy=Event.q.name)[:10]

        return dict(user=user, search_form=artist_search_form, events=events)

    artists = Artists()

    venues = Venues()

    events = Events()

    users = Users()

    importers = Importers()

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
