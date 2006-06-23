import turbogears
from turbogears import controllers, expose, redirect
from turbogears import identity
from turbogears import widgets as w
from turbogears import validators as v

from model import Venue, Event, hub
from sqlobject import SQLObjectNotFound, LIKE, func, AND
from datetime import date
import util

class SearchBox(w.WidgetsList):
    search = util.BRAutoCompleteField("/venues/dynsearch")

venue_search_form = w.ListForm(fields=SearchBox(), name="search",
    submit_text="Search")


class Venues(controllers.Controller, util.RestAdapter):

    @expose(allow_json=True)
    def dynsearch(self, name):
        return util.dynsearch(Venue, name)

    @expose(template=".templates.venue.list")
    def list(self):
        venues = Venue.select(AND(Venue.q.verified == True, Venue.q.active == True),
            orderBy=Venue.q.name)
        for v in venues:
            v.eventcount = Event.select(AND(Event.q.venueID == v.id,
                Event.q.date >= date.today())).count()
        return dict(venues=venues)

    @expose(template=".templates.venue.show")
    def show(self, id):
        try:
            v = Venue.get(id)
        except SQLObjectNotFound:
            turbogears.flash("Venue ID not found")
            redirect(turbogears.url("/venues/list"))

        past_events = Event.select(AND(Event.q.venueID == v.id,
            Event.q.date < date.today()),orderBy=Event.q.date)[:5]
        future_events = Event.select(AND(Event.q.venueID == v.id,
            Event.q.date >= date.today()),orderBy=Event.q.date)
        return dict(v=v, past_events=past_events, future_events=future_events)

    @expose(template=".templates.venue.edit")
    def edit(self, id=0, name="", addr="", url=""):
        if id:
            try:
                v = Venue.get(id)
                name = v.name
                addr = v.address
                url = v.url
            except SQLObjectNotFound:
                turbogears.flash("Invalid ID")
                redirect(turbogears.url("/venues/list"))
        return dict(id=id, name=name, addr=addr, url=url)

    @expose()
    def save(self, submit, id, name, addr="", url=""):
        try:
            v = Venue.get(id)
            v.name = name
            v.address = addr
            v.url = url
            turbogears.flash("Updated")
        except SQLObjectNotFound:
            v = Venue(name=name, address=addr, url=url)
            turbogears.flash("Added to DB")
        redirect(turbogears.url("/venues/%s" % v.id))

    @expose()
    def delete(self, id):
        if Event.select(Event.q.venueID == id).count():
            turbogears.flash("Delete failed")
        else:
            Venue.delete(id)
            turbogears.flash("Deleted")
        redirect(turbogears.url("/venues/list"))
