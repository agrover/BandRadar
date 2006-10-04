import cherrypy
import turbogears
from turbogears import controllers, expose, redirect
from turbogears import identity
from turbogears import widgets as w
from turbogears import validators as v
from model import Event, Venue, Artist, hub
from sqlobject import SQLObjectNotFound, AND, OR
from datetime import date
import MBL
import WWBL

class Merc(w.WidgetsList):
    url = w.TextField(label="URL", attrs={'size':90},
        validator=v.All(v.NotEmpty, v.URL))

class WWeek(w.WidgetsList):
    thedate = w.CalendarDatePicker(label="Date")
    do_week = w.CheckBox(label="Import whole week")

merc = w.TableForm(fields=Merc(), name="merc", submit_text="Go")
wweek = w.TableForm(fields=WWeek(), name="wweek", submit_text="Go")

class Importers(controllers.Controller, identity.SecureResource):
    require = identity.in_group("admin")

    @expose(template="bandradar.templates.webimport")
    def webimport(self, tg_errors=None):
        if tg_errors:
            turbogears.flash("Entry error")
        return dict(merc_form=merc, wweek_form=wweek)

    @expose()
    @turbogears.validate(form=merc)
    @turbogears.error_handler(webimport)
    def importmercury(self, url):

        venues = MBL.MBL().parse_week(url)
        self.import_to_db(venues)
        turbogears.flash("Mercury Imported")
        redirect(turbogears.url("/importers/review"))

    @expose()
    @turbogears.validate(form=wweek)
    @turbogears.error_handler(webimport)
    def importwweek(self, thedate, do_week=False):
        if not do_week:
            venues = WWBL.WWBL().parse_day(thedate)
        else:
            venues = WWBL.WWBL().parse_week(thedate)
        self.import_to_db(venues)
        turbogears.flash("WWeek Imported")
        redirect(turbogears.url("/importers/review"))


    def import_to_db(self, venues):
        e_counter = 0

        for venue in venues:

            try:
                v = Venue.byName(venue['name'])
            except SQLObjectNotFound:
                v = Venue(name=venue['name'], added_by=identity.current.user)

                optional_fields = ("address", "phone")
                for field in optional_fields:
                    try:
                        v.set(**{field:venue[field]})
                    except KeyError:
                        pass

            for event in venue["events"]:
                time = event.get("time")
                cost = event.get("cost")

                db_events = Event.selectBy(date=event["date"],
                    time=time, venue=v)
                # must be unique
                if db_events.count():
                    e = list(db_events)[0]
                else:
                    e = Event(venue=v, name=event["name"],
                        date=event["date"], time=time, cost=cost,
                        added_by=identity.current.user)

                for artist in event["artists"]:
                    try:
                        a = Artist.byName(artist)
                    except SQLObjectNotFound:
                        a = Artist(name=artist, added_by=identity.current.user)
                    if not e.id in [existing.id for existing in a.events]:
                        a.addEvent(e)

    @expose(template="bandradar.templates.importreview")
    def review(self):
        try_to_show = 25
        total = Event.select(Event.q.verified == False).count()
        events = Event.select(Event.q.verified == False,
            orderBy=Event.q.name)[:try_to_show]
        shown = min(total, try_to_show)
        return dict(events=events, shown=shown, total=total)

    @expose()
    def reviewsubmit(self, submit, **kw):
        if submit == "Import Checked":
            self.review_import(**kw)
            turbogears.flash("Imported")
        else:
            self.review_delete(**kw)
            turbogears.flash("Deleted")
        redirect(turbogears.url("/importers/review"))

    def review_import(self, **kw):
        e_counter = 0
        while True:
            try:
                e_id = kw["eid"+str(e_counter)]
            except KeyError:
                break
            e_counter += 1
            if not kw.has_key("accept"+e_id):
                continue
            e = Event.get(e_id)
            e.verified = True
            v = e.venue
            v.verified = True
            for artist in e.artists:
                artist.verified = True

    def delete_event(self, event):
        for a in event.artists:
            event.removeArtist(a)
            a.destroy_if_unused()
        v = event.venue
        if not Event.select(Event.q.venueID == v.id).count():
            v.destroySelf()
        event.destroySelf()

    def review_delete(self, **kw):
        e_counter = 0
        while True:
            try:
                e_id = kw["eid"+str(e_counter)]
            except KeyError:
                break
            e_counter += 1
            if not kw.has_key("accept"+e_id):
                continue
            e = Event.get(e_id)
            self.delete_event(e)

    @expose()
    def reviewpurge(self):
        new_events = Event.select(Event.q.verified == False)
        for event in new_events:
            self.delete_event(event)
        redirect(turbogears.url("/importers/review"))
