import turbogears
from turbogears import controllers, expose, redirect
from turbogears import identity
from turbogears import widgets as w
from turbogears import validators as v

from model import Venue, Event, hub
from sqlobject import SQLObjectNotFound, LIKE, func, AND
from datetime import date
import util

class VenueForm(w.WidgetsList):
    id = w.HiddenField(validator=v.Int)
    name = w.TextField(validator=v.NotEmpty)
    description = w.TextArea(rows=3)
    address = w.TextField()
    phone = w.TextField()
    url = w.TextField(label="Website", attrs=dict(size=50),
        validator=v.Any(v.URL, v.Empty))

venue_form = w.TableForm(fields=VenueForm(), name="venue", submit_text="Save")

class SearchBox(w.WidgetsList):
    search = util.BRAutoCompleteField("/venues/dynsearch")

venue_search_form = w.ListForm(fields=SearchBox(), name="search",
    submit_text="Search")


class Venues(controllers.Controller, util.RestAdapter):

    @expose(allow_json=True)
    def dynsearch(self, name):
        return util.dynsearch(Venue, name)

    @expose(template=".templates.venue.search_results")
    @turbogears.validate(form=venue_search_form)
    def search(self, search, tg_errors=None):
        results = util.search(Venue, search['text'], tg_errors)
        return dict(venues=results, venue_search_form=venue_search_form)

    @expose(template=".templates.venue.list")
    def list(self):
        venues = Venue.select(AND(Venue.q.verified == True, Venue.q.active == True),
            orderBy=Venue.q.name)
        for v in venues:
            v.eventcount = Event.select(AND(Event.q.venueID == v.id,
                Event.q.date >= date.today())).count()
        return dict(venues=venues, venue_search_form=venue_search_form)

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
        return dict(venue=v, past_events=past_events, future_events=future_events)

    @expose(template=".templates.venue.edit")
    def edit(self, id=0):
        if id:
            try:
                v = Venue.get(id)
            except SQLObjectNotFound:
                turbogears.flash("Invalid ID")
                redirect(turbogears.url("/venues/list"))
        else:
            v = {}
        return dict(venue_form=venue_form, form_vals=v)

    @expose()
    @turbogears.validate(form=venue_form)
    @turbogears.error_handler(edit)
    def save(self, id=0, **kw):
        if id:
            try:
                v = Venue.get(id)
                v.set(**kw)
                turbogears.flash("Updated")
            except SQLObjectNotFound:
                turbogears.flash("Update Error")
        else:
            v = Venue(added_by=identity.current.user, **kw)
            turbogears.flash("Added")
        redirect(turbogears.url("/venues/%s" % v.id))

    @expose()
    def delete(self, id):
        if Event.select(Event.q.venueID == id).count():
            turbogears.flash("Delete failed")
        else:
            Venue.delete(id)
            turbogears.flash("Deleted")
        redirect(turbogears.url("/venues/list"))
