import turbogears
from turbogears import controllers, expose, redirect
from turbogears import identity
from turbogears import widgets as w
from turbogears import validators as v

from model import Venue, Event, hub
from sqlobject import SQLObjectNotFound, LIKE, func, AND
from datetime import date
from bandradar import util
from bandradar.widgets import BRAutoCompleteField, googlemap

class VenueForm(w.WidgetsList):
    id = w.HiddenField(validator=v.Int)
    name = w.TextField(validator=v.NotEmpty(strip=True))
    description = w.TextArea(rows=3)
    address = w.TextField()
    zip_code = w.TextField(label="Zip Code",
        attrs=dict(size=10, maxlength=10),
        validator=v.PostalCode(strip=True))
    phone = w.TextField()
    url = w.TextField(label="Website", attrs=dict(size=50),
        validator=v.Any(v.URL, v.Empty))
    myspace = w.TextField(label="MySpace", attrs=dict(maxlength=40),
        help_text="e.g. myspace.com/abc, enter abc")

class VenueSchema(v.Schema):
    chained_validators = [util.UniqueName(Venue)]

venue_form = w.TableForm(fields=VenueForm(), name="venue", submit_text="Save",
                            validator=VenueSchema())

class SearchBox(w.WidgetsList):
    search = BRAutoCompleteField("/venues/dynsearch")

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
        conn = hub.getConnection()
        results = conn.queryAll("""
            select venue.id, venue.name, count(event.id)
            from venue, event
            where venue.id = event.venue_id
                and event.date >= CURRENT_DATE
            group by venue.id, venue.name
            order by venue.name
            """)

        tracked_venues = []
        if identity.current.user:
            tracked_venues = [v.id for v in identity.current.user.venues]

        venue_list = []
        for id, name, count in results:
            venue_list.append(dict(name=name, id=id, eventcount=count))
        return dict(venues=venue_list, count=len(venue_list),
            venue_search_form=venue_search_form,
            tracked_venues=tracked_venues)

    @expose(template=".templates.venue.show")
    def show(self, id):
        try:
            v = Venue.get(id)
            is_tracked = identity.current.user and e in identity.current.user.venues
        except SQLObjectNotFound:
            turbogears.flash("Venue ID not found")
            redirect(turbogears.url("/venues/list"))

        past_events = v.events.filter(Event.q.date < date.today()).orderBy('-date')[:5]
        past_events = list(reversed(list(past_events)))
        future_events = v.events.filter(Event.q.date >= date.today()).orderBy('date')

        return dict(venue=v, past_events=past_events, future_events=future_events,
            description=util.desc_format(v.description), googlemap=googlemap,
            tracked_count=v.users.count(), is_tracked=is_tracked)

    @expose(template=".templates.venue.edit")
    @identity.require(identity.in_group("admin"))
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
    @identity.require(identity.in_group("admin"))
    @turbogears.validate(form=venue_form)
    @turbogears.error_handler(edit)
    def save(self, id=0, **kw):
        if id:
            try:
                v = Venue.get(id)
                v.set(**v.clean_dict(kw))
                turbogears.flash("Updated")
            except SQLObjectNotFound:
                turbogears.flash("Update Error")
        else:
            v = Venue(added_by=identity.current.user, **Venue.clean_dict(kw))
            turbogears.flash("Added")
        redirect(turbogears.url("/venues/%s" % v.id))

    @expose()
    @identity.require(identity.not_anonymous())
    def track(self, id, viewing="no"):
        u = identity.current.user
        try:
            v = Venue.get(id)
            if v not in u.venues:
                u.addVenue(v)
        except SQLObjectNotFound:
            turbogears.flash("Venue not found")
            redirect("/")
        if viewing == "no":
            util.redirect_previous()
        else:
            util.redirect("/venues/%s" % v.id)

    @expose()
    @identity.require(identity.not_anonymous())
    def untrack(self, id, viewing="no"):
        u = identity.current.user
        try:
            v = Venue.get(id)
            if v in u.venues:
                u.removeVenue(v)
        except SQLObjectNotFound:
            turbogears.flash("Venue not found")
            redirect("/")
        if viewing == "no":
            util.redirect_previous()
        else:
            util.redirect("/venues/%s" % v.id)

    @expose("json", fragment=True)
    @identity.require(identity.not_anonymous())
    def dyntrack(self, id, tracked):
        u = identity.current.user
        ret = "Error"
        try:
            v = Venue.get(id)
            if not tracked == "true" and v not in u.venues:
                u.addVenue(v)
                ret = "Tracked"
            if tracked == "true" and v in u.venues:
                u.removeVenue(v)
                ret = "Untracked"
        except SQLObjectNotFound:
            pass
        return ret

    @expose()
    @identity.require(identity.in_group("admin"))
    def delete(self, id):
        try:
            v = Venue.get(id)
            v.destroySelf()
            turbogears.flash("Deleted")
        except SQLObjectNotFound:
            turbogears.flash("Delete failed")
        redirect(turbogears.url("/venues/list"))
