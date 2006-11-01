import turbogears
from turbogears import controllers, expose, redirect
from turbogears import identity
from turbogears import database
from turbogears import widgets as w
from turbogears import validators as v

from model import Event, Venue, Artist, hub
from sqlobject import SQLObjectNotFound, LIKE, func, AND
from datetime import date, datetime, timedelta
import util
from cgi import escape

class EventForm(w.WidgetsList):
    id = w.HiddenField(validator=v.Int)
    name = w.TextField(label="Event Name", help_text="If different from artists' names")
    artists = w.TextArea(help_text="Enter artists, one per line", validator=v.NotEmpty(strip=True), rows=3, cols=30)
    venue = util.BRAutoCompleteField("/venues/dynsearch", label="Venue")
    date = w.CalendarDatePicker(not_empty=True)
    time = w.TextField(attrs=dict(maxlength=40))
    cost = w.TextField(attrs=dict(maxlength=120))
    ages = w.TextField(attrs=dict(maxlength=40))
    description = w.TextArea(rows=3)
    url = w.TextField(label="Website", attrs=dict(size=50, maxlength=256),
        validator=v.Any(v.URL, v.Empty))

event_form = w.TableForm(fields=EventForm(), name="event", submit_text="Save")

class SearchBox(w.WidgetsList):
    search = util.BRAutoCompleteField("/events/dynsearch")

event_search_form = w.ListForm(fields=SearchBox(), name="search",
    submit_text="Search")


class Events(controllers.Controller, util.RestAdapter):

    @expose(allow_json=True)
    def dynsearch(self, name):
        return util.dynsearch(Event, name)

    @expose(template=".templates.event.search_results")
    @turbogears.validate(form=event_search_form)
    def search(self, search, tg_errors=None):
        results = util.search(Event, search['text'], tg_errors)
        return dict(events=results, event_search_form=event_search_form)

    @expose(template=".templates.event.list")
    def list(self, listby="today", orderby="alpha"):

        def events_in_period(day_delta, day_count=1):
            day_result = []
            start_date = date.today() + timedelta(day_delta)
            where_clause = AND(Event.q.date >= start_date, Event.q.approved != None)
            if day_count != 0:
                end_date = start_date + timedelta(day_count-1)
                where_clause = AND(where_clause, Event.q.date <= end_date)
            events = Event.select(where_clause, orderBy=(Event.q.date, Event.q.name))
            return events

        if listby == "today":
            result = events_in_period(0)
        elif listby == "tomorrow":
            result = events_in_period(1)
        elif listby == "yesterday":
            result = events_in_period(-1)
        elif listby == "week":
            result = events_in_period(0, 7)
        elif listby == "all":
            result = events_in_period(0, 0)

        return dict(events=result, count=result.count(), 
            listby=listby, event_search_form=event_search_form)

    @expose(template=".templates.event.show")
    def show(self, id):
        try:
            e = Event.get(id)
            if not e.artists.count():
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
                form_vals = database.so_to_dict(e)
                form_vals['artists'] = "\n".join([a.name for a in e.artists])
                form_vals['venue'] = dict(text=e.venue.name)
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
            v = Venue(name=kw['venue']['text'], added_by=identity.current.user)

        artists = kw.pop('artists', None)
        artist_list = [artist.strip() for artist in artists.split('\n')]
        # elim blank items in list
        artist_list = [artist for artist in artist_list if artist]
        name = kw.get('name', None)
        if not name:
            name = ", ".join(artist_list)

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
                added_by=identity.current.user)
            flash_msg = "added"

        del kw['venue']
        e.set(**e.clean_dict(kw))
        e.name = name
        e.venue = v
        # add new artists
        for artist in artist_list:
            try:
                a = Artist.byName(artist)
                if not a in e.artists:
                    e.addArtist(a)
            except SQLObjectNotFound:
                a = Artist(name=artist, added_by=identity.current.user)
                e.addArtist(a)
        # remove old artists
        for artist in e.artists:
            if artist.name not in artist_list:
                e.removeArtist(artist)
                artist.destroy_if_unused()
        turbogears.flash("Event %s" % flash_msg)
        redirect(turbogears.url("/events/%s" % e.id))

    @expose()
    @identity.require(identity.in_group("admin"))
    def delete(self, id):
        try:
            e = Event.get(id)
            e.destroySelf()
            turbogears.flash("Deleted")
        except SQLObjectNotFound:
            turbogears.flash("Delete failed")
        redirect(turbogears.url("/events/list"))
