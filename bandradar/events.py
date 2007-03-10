from turbogears import controllers, expose, redirect, flash, validate, error_handler
from turbogears import identity
from turbogears import widgets as w
from turbogears import validators as v

from model import Event, Venue, Artist, Attendance, UpdateLog
from sqlobject import SQLObjectNotFound, LIKE, func, AND
from datetime import date, datetime, timedelta
from cgi import escape

from bandradar import util
from bandradar.widgets import (BRAutoCompleteField, BRCalendarDatePicker,
                               artist_list, googlemap)

class EventForm(w.WidgetsList):
    id = w.HiddenField(validator=v.Int)
    name = w.TextField(label="Event Name", help_text="If different from artists' names")
    artists = w.TextArea(help_text="Enter artists, one per line", validator=v.NotEmpty(strip=True), rows=3, cols=30)
    venue = BRAutoCompleteField("/venues/dynsearch", label="Venue")
    date = BRCalendarDatePicker(not_empty=True)
    time = w.TextField(attrs=dict(maxlength=40))
    cost = w.TextField(attrs=dict(maxlength=120))
    ages = w.TextField(attrs=dict(maxlength=40))
    description = w.TextArea(rows=3)
    url = w.TextField(label="Website", attrs=dict(size=50, maxlength=256),
        validator=v.Any(v.URL, v.Empty))

event_form = w.TableForm(fields=EventForm(), name="event", submit_text="Save")

class SearchBox(w.WidgetsList):
    search = BRAutoCompleteField("/events/dynsearch")

event_search_form = w.ListForm(fields=SearchBox(), name="search",
    submit_text="Search")

class Events(controllers.Controller, util.RestAdapter):

    @expose("json")
    def dynsearch(self, name):
        return util.dynsearch(Event, name)

    @expose(template=".templates.event.search_results")
    @validate(form=event_search_form)
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
        except SQLObjectNotFound:
            flash("Event not found")
            util.redirect("/events/list")
        return dict(event=e, artist_list=artist_list, googlemap=googlemap,
            description=util.desc_format(e.description))

    @expose()
    @identity.require(identity.not_anonymous())
    def edit(self, id=0, **kw):
        form_vals = {}
        template = ".templates.event.add"
        if id:
            try:
                e = Event.get(id)
                form_vals = util.so_to_dict(e)
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
        try:
            v = Venue.get(int(kw['venue_prefill']))
            flash(form_vals)
            form_vals['venue'] = dict(text=v.name)
        except (SQLObjectNotFound, KeyError):
            pass

        return dict(tg_template=template, event_form=event_form, form_vals=form_vals)

    @expose()
    @validate(form=event_form)
    @error_handler(edit)
    @identity.require(identity.not_anonymous())
    def save(self, id, **kw):
        try:
            v = Venue.byName(kw['venue']['text'])
        except SQLObjectNotFound:
            v = Venue(name=kw['venue']['text'], added_by=identity.current.user)

        artists = kw.pop('artists', None)
        artist_name_list = [artist.strip() for artist in artists.split('\n')]
        # elim blank items in list
        artist_name_list = [artist for artist in artist_name_list if artist]
        name = kw.get('name', None)
        if not name:
            name = ", ".join(artist_name_list)

        # updating
        if id:
            try:
                e = Event.get(id)
                flash_msg = "updated"
            except SQLObjectNotFound:
                flash("Database error, please try again")
                redirect("/")
        # inserting
        else:
            e = Event(name=name, date=kw['date'], time=kw['time'], venue=v,
                added_by=identity.current.user)
            flash_msg = "added"

        del kw['venue']
        e.set(**e.clean_dict(kw))
        e.name = name
        e.venue = v
        old_artists = set([a.name for a in e.artists])
        # add new artists
        artist_list = []
        for artist in artist_name_list:
            try:
                a = Artist.byNameI(artist)
                if not a in e.artists:
                    e.addArtist(a)
            except SQLObjectNotFound:
                a = Artist(name=artist, added_by=identity.current.user)
                e.addArtist(a)
            artist_list.append(a)
        # remove old artists
        for artist in e.artists:
            if artist not in artist_list:
                e.removeArtist(artist)
                artist.destroy_if_unused()
        new_artists = set([a.name for a in e.artists])
        if old_artists != new_artists and e.approved:
            u = UpdateLog(
                changed_by=identity.current.user.id,
                table_name="artist_event",
                table_id=e.id,
                attrib_name="artists",
                attrib_old_value=old_artists,
                attrib_new_value=new_artists
                )
        flash("Event %s" % flash_msg)
        util.redirect("/events/%s" % e.id)

    @expose()
    @identity.require(identity.not_anonymous())
    def track(self, id, viewing="no", planning=False, went=False):
        u = identity.current.user
        try:
            e = Event.get(id)
            try:
                att = Attendance.selectBy(user=u, event=e)[0]
            except IndexError:
                att = Attendance(user=u, event=e)
            att.planning_to_go = planning
            att.attended = went
        except SQLObjectNotFound:
            flash("Event not found")
            redirect("/")
        if viewing == "no":
            util.redirect_previous()
        else:
            util.redirect("/events/%s" % e.id)

    @expose()
    @identity.require(identity.not_anonymous())
    def untrack(self, id, viewing="no"):
        u = identity.current.user
        try:
            e = Event.get(id)
            atts = Attendance.selectBy(user=u, event=e)
            for att in atts:
                att.destroySelf()
        except SQLObjectNotFound:
            flash("Event not found")
            redirect("/")
        if viewing == "no":
            util.redirect_previous()
        else:
            util.redirect("/events/%s" % e.id)

    @expose()
    @identity.require(identity.in_group("admin"))
    def delete(self, id):
        try:
            e = Event.get(id)
            e.destroySelf()
            flash("Deleted")
        except SQLObjectNotFound:
            flash("Delete failed")
        util.redirect("/events/list")
