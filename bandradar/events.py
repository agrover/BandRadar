import turbogears
from turbogears import controllers, expose, redirect
from turbogears import identity
from turbogears import widgets as w
from turbogears import validators as v
from model import Event, Venue, Artist, hub
from sqlobject import SQLObjectNotFound, LIKE, func, AND
import util
from cgi import escape

class AutoCompleteValidator(v.Schema):
    def _to_python(self, value, state):
        text = value['text']
        value['text'] = v.NotEmpty(strip=True).to_python(text)
        return value

class EventForm(w.WidgetsList):
    id = w.HiddenField(validator=v.Int)
    name = w.TextField()
    artists = w.TextField(help_text="Enter artists, comma-separated", validator=v.NotEmpty(strip=True))
    date = w.CalendarDatePicker(not_empty=True)
    time = w.TextField()
    cost = w.TextField()
    ages = w.TextField()
    description = w.TextArea(rows=3)
    url = w.TextField(label="Website", attrs=dict(size=50),
        validator=v.Any(v.URL, v.Empty))
    venue = w.AutoCompleteField(label="Venue",
        search_controller="/venues/dynsearch",
        search_param="name",
        result_name="results",
        only_suggest=True,
        validator=AutoCompleteValidator(),
        attrs={'size':20})

event_form = w.TableForm(fields=EventForm(), name="event", submit_text="Save")


class Events(controllers.Controller, util.RestAdapter):

    @expose(template=".templates.eventlist")
    def list(self, listby="all"):
        e = Event.select(AND(Event.q.verified == True, Event.q.active == True),
            orderBy=Event.q.name)
        return dict(events=e)

    @expose(template=".templates.eventshow")
    def show(self, id):
        try:
            e = Event.get(id)
            if not len(e.artists):
                artisthtml = "<strong>None</strong>"
            else:
                htmlstr = "<a href=\"/artists/%s\">%s</a>"
                artist_html_list = [ htmlstr % (a.id, escape(a.name)) for a in e.artists ]
                artisthtml = ", ".join(artist_html_list)
        except SQLObjectNotFound:
            turbogears.flash("Event not found")
            redirect(turbogears.url("/events/list"))
        return dict(event=e, artisthtml=artisthtml)

    @expose()
    @identity.require(identity.not_anonymous())
    def edit(self, id=0, tg_errors=None, **kw):
        form_vals = {}
        template = ".templates.eventadd"
        if id:
            try:
                e = Event.get(id)
                artists_str = ", ".join([a.name for a in e.artists])
                form_vals = dict(id=id, name=e.name, date=e.date, cost=e.cost,
                    ages=e.ages, description=e.description, url=e.url,
                    time=e.time, venue=dict(text=e.venue.name),
                    artists=artists_str)
                    # use different template since we're editing existing
                template = ".templates.eventedit"
            except SQLObjectNotFound:
                pass
        else:
            form_vals = dict(id=id)
        try:
            a = Artist.get(int(kw['artist_prefill']))
            form_vals['artists'] = a.name
        except (SQLObjectNotFound, KeyError):
            pass
        form_vals.update(kw)
        return dict(tg_template=template, event_form=event_form, form_vals=form_vals)

    @expose()
    @turbogears.validate(form=event_form)
    @turbogears.error_handler(edit)
    @identity.require(identity.not_anonymous())
    def save(self, id=0, name="", description="", **kw):
        if id:
            try:
                e = Event.get(id)
                e.set(**kw)
                try:
                    v = Venue.byName(venue['text'])
                except SQLObjectNotFound:
                    v = Venue(name=venue['text'], verified=True)
                e.venue = v
                #split/add artists
                #addedby
                turbogears.flash("Updated")
            except SQLObjectNotFound:
                e = Event(name=name, description=description)

                turbogears.flash("Added to DB")
        else:
            e = Event(name=name, description=description)
            turbogears.flash("Added to DB")
        redirect(turbogears.url("/events/%s" % e.id))

    @expose()
    @identity.require(identity.in_group("admin"))
    def delete(self, id):
        try:
            e = Event.get(id)
            for a in e.artists:
                e.removeArtist(a)
            e.destroySelf()
            turbogears.flash("Deleted")
        except SQLObjectNotFound:
            turbogears.flash("Delete failed")
        redirect(turbogears.url("/events/list"))
