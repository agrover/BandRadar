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
    venue = util.BRAutoCompleteField("/venues/dynsearch", label="Venue")

event_form = w.TableForm(fields=EventForm(), name="event", submit_text="Save")

class SearchBox(w.WidgetsList):
    search = util.BRAutoCompleteField("/events/dynsearch")

event_search_form = w.ListForm(fields=SearchBox(), name="search",
    submit_text="Search")


class Events(controllers.Controller, util.RestAdapter):

    @expose(allow_json=True)
    def dynsearch(self, name):
        return util.dynsearch(Event, name)

    @expose(template=".templates.event.list")
    def list(self, listby="all"):
        e = Event.select(AND(Event.q.verified == True, Event.q.active == True),
            orderBy=Event.q.name)
        return dict(events=e, event_search_form=event_search_form)

    @expose(template=".templates.event.show")
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
    def edit(self, id=0, **kw):
        form_vals = {}
        template = ".templates.event.add"
        if id:
            try:
                e = Event.get(id)
                artists_str = ", ".join([a.name for a in e.artists])
                form_vals = dict(id=id, name=e.name, date=e.date, cost=e.cost,
                    ages=e.ages, description=e.description, url=e.url,
                    time=e.time, venue=dict(text=e.venue.name),
                    artists=artists_str)
                    # use different template since we're editing existing
                template = ".templates.event.edit"
            except SQLObjectNotFound:
                pass
        else:
            form_vals = dict(id=id)
        try:
            a = Artist.get(int(kw['artist_prefill']))
            form_vals['artists'] = a.name
        except (SQLObjectNotFound, KeyError):
            pass
        return dict(tg_template=template, event_form=event_form, form_vals=form_vals)

    @expose()
    @turbogears.validate(form=event_form)
    @turbogears.error_handler(edit)
    @identity.require(identity.not_anonymous())
    def save(self, id, **kw):
        try:
            v = Venue.byName(kw['venue']['text'])
        except SQLObjectNotFound:
            v = Venue(name=kw['venue']['text'], added_by=util.who_added())

        artists = kw.get('artists')
        artist_list = [artist.strip() for artist in artists.split(",")]
        name = kw.get('name')
        if not name:
            name = artists

        # updating
        if id:
            try:
                e = Event.get(id)
                flash_msg = "updated"
            except SQLObjectNotFound:
                turbogears.flash("Database error, please try again")
                redirect(turbogears.url("/"))
        # inserting
        else:
            e = Event(name=name, date=kw['date'], time=kw['time'], venue=v,
                added_by=util.who_added())
            flash_msg = "added"

        del kw['artists']
        del kw['venue']
        e.set(**kw)
        e.name = name
        e.venue = v
        for artist in artist_list:
            try:
                a = Artist.byName(artist)
                if not a in e.artists:
                    e.addArtist(a)
            except SQLObjectNotFound:
                a = Artist(name=artist, added_by=util.who_added())
                e.addArtist(a)
        turbogears.flash("Event %s" % flash_msg)
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
