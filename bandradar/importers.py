import cherrypy
import turbogears
from turbogears import controllers, expose, redirect
from turbogears import identity
from turbogears import widgets as w
from turbogears import validators as v
from model import Event, Venue, Artist, hub
from sqlobject import SQLObjectNotFound, AND, OR
from datetime import date, datetime
import MBL
import WWBL
import pollstar

class Merc(w.WidgetsList):
    url = w.TextField(label="URL", attrs=dict(size=60),
        validator=v.All(v.NotEmpty, v.URL))

class WWeek(w.WidgetsList):
    thedate = w.CalendarDatePicker(label="Date")
    do_week = w.CheckBox(label="Import whole week")

merc_form = w.TableForm(fields=Merc(), name="merc", submit_text="Go")
wweek_form = w.TableForm(fields=WWeek(), name="wweek", submit_text="Go")

class Importers(controllers.Controller, identity.SecureResource):
    require = identity.in_group("admin")

    @expose(template=".templates.webimport")
    def webimport(self, tg_errors=None):
        if tg_errors:
            turbogears.flash("Entry error")
        return dict(merc_form=merc_form, wweek_form=wweek_form)
    @expose()
    @turbogears.validate(form=merc_form)
    @turbogears.error_handler(webimport)
    def importmercury(self, url):

        venues = MBL.parse_week(url)
        self.import_to_db(venues)
        turbogears.flash("Mercury Imported")
        redirect(turbogears.url("/importers/review"))

    @expose()
    @turbogears.validate(form=wweek_form)
    @turbogears.error_handler(webimport)
    def importwweek(self, thedate, do_week=False):
        if not do_week:
            venues = WWBL.parse_day(thedate)
        else:
            venues = WWBL.parse_week(thedate)
        self.import_to_db(venues)
        turbogears.flash("WWeek Imported")
        redirect(turbogears.url("/importers/review"))

    @expose()
    def importpollstar(self):
        venues = pollstar.parse_all()
        self.import_to_db(venues)
        turbogears.flash("Pollstar Imported")
        redirect(turbogears.url("/importers/review"))

    def _set_optional_fields(self, obj, in_dict, field_list):
        model = obj.__class__
        for field in field_list:
            try:
                # truncate if too long
                field_len = getattr(model.q, field).column.length
                in_dict[field] = in_dict[field][:field_len]
                obj.set(**{field:in_dict[field]})
            except (KeyError, TypeError):
                pass

    def import_to_db(self, venues):
        for venue in venues:
            try:
                v = Venue.byNameI(venue['name'])
            except SQLObjectNotFound:
                v = Venue(name=venue['name'], added_by=identity.current.user)
                self._set_optional_fields(v, venue, ("address", "phone"))

            for event in venue["events"]:
                time = event.get("time")
                db_events = Event.selectBy(date=event["date"],
                    time=time, venue=v)
                # must be unique, due to db constraint
                if db_events.count():
                    e = db_events[0]
                else:
                    e = Event(venue=v, name=event["name"],
                        date=event["date"], time=time,
                        added_by=identity.current.user)
                    self._set_optional_fields(e, event, ("cost", "ages"))

                for artist in event["artists"]:
                    try:
                        a = Artist.byNameI(artist)
                    except SQLObjectNotFound:
                        a = Artist(name=artist, added_by=identity.current.user)
                    if not e.id in [existing.id for existing in a.events]:
                        a.addEvent(e)

    @expose(template=".templates.importreview")
    def review(self):
        try_to_show = 100
        result = Event.select(Event.q.approved == None, orderBy=(Event.q.cost, Event.q.name))
        total = result.count()
        shown = min(total, try_to_show)
        events = result[:shown]
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
        now = datetime.now()
        while True:
            try:
                e_id = kw["eid"+str(e_counter)]
            except KeyError:
                break
            e_counter += 1
            if not kw.has_key("accept"+e_id):
                continue
            e = Event.get(e_id)
            e.approved = now
            v = e.venue
            v.approved = now
            for artist in e.artists:
                artist.approved = now

    def delete_event(self, event):
        for a in event.artists:
            event.removeArtist(a)
            a.destroy_if_unused()
        v = event.venue
        event.destroySelf()
        v.destroy_if_unused()

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
        new_events = Event.select(Event.q.approved == None)
        for event in new_events:
            self.delete_event(event)
        redirect(turbogears.url("/importers/review"))

    @expose(template=".templates.reviewdupes")
    def reviewdupes(self):
        conn = hub.getConnection()
        dupe_results = conn.queryAll("""
            select name, date, venue_id, count(*)
            from event
            group by venue_id, date, name
            having count(*) > 1
            """)
        dupes = []
        for name, date, venue_id, count in dupe_results:
            dupes.extend(list(Event.selectBy(date=date, venueID=venue_id)))
        return dict(events=dupes)
