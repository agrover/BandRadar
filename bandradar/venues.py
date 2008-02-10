from turbogears import controllers, expose, validate, error_handler, flash
from turbogears import identity
from turbogears import widgets as w
from turbogears import validators as v

from model import Venue, Event, hub
from sqlobject import SQLObjectNotFound, LIKE, func, AND
from sqlobject.main import SQLObjectIntegrityError
from datetime import date, datetime
import urllib
import util
from widgets import BRAutoCompleteField, googlemap
from importers import venue_fixup_dict

class VenueForm(w.WidgetsList):
    id = w.HiddenField(validator=v.Int)
    name = w.TextField(validator=v.NotEmpty(strip=True), attrs=dict(size=40))
    description = w.TextArea(rows=6, cols=40,
        validator=v.UnicodeString(strip=True))
    address = w.TextField(attrs=dict(size=40))
    zip_code = w.TextField(label="Zip Code",
        attrs=dict(size=10, maxlength=10),
        validator=v.PostalCode(strip=True))
    phone = w.TextField(validator=v.PhoneNumber())
    url = w.TextField(label="Website", attrs=dict(size=50),
        validator=v.Any(v.URL, v.Empty))
    myspace = w.TextField(label="MySpace", attrs=dict(maxlength=40),
        help_text="either myspace.com/abc or abc")

class VenueSchema(v.Schema):
    chained_validators = [util.UniqueName(Venue)]

venue_form = w.TableForm(fields=VenueForm(), name="venue", submit_text="Save",
                            validator=VenueSchema())

class VenueController(controllers.Controller, util.RestAdapter):

    @expose(allow_json=True)
    def dynsearch(self, name):
        return dict(results=util.dynsearch(Venue, name))

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
            tracked_venues=tracked_venues)

    @expose(template=".templates.venue.show")
    def show(self, id, list_all=0):
        try:
            v = Venue.get(id)
        except SQLObjectNotFound:
            flash("Venue ID not found")
            util.redirect("/venues/list")
        except ValueError:
            try:
                v = Venue.byNameI(urllib.unquote_plus(id))
            except SQLObjectNotFound:
                flash("Venue ID not found")
                util.redirect("/venues/list")
            
        is_tracked = identity.current.user and v in identity.current.user.venues

        past_events = v.past_events.orderBy('-date')
        if not list_all:
            past_events = past_events[:5]
        future_events = v.future_events.orderBy('date')

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
                flash("Invalid ID")
                util.redirect("/venues/list")
        else:
            v = {}
        return dict(venue_form=venue_form, form_vals=v)

    @expose()
    @identity.require(identity.in_group("admin"))
    @validate(form=venue_form)
    @error_handler(edit)
    def save(self, id=0, **kw):
        if id:
            try:
                v = Venue.get(id)
                v.set(**v.clean_dict(kw))
                flash("Updated")
            except SQLObjectNotFound:
                flash("Update Error")
        else:
            v = Venue(added_by=identity.current.user, **Venue.clean_dict(kw))
            flash("Added")
        v.approved = datetime.now()
        util.redirect("/venues/%s" % v.id)

    @expose()
    @identity.require(identity.not_anonymous())
    def track(self, id, viewing="no"):
        u = identity.current.user
        try:
            v = Venue.get(id)
            if v not in u.venues:
                u.addVenue(v)
        except SQLObjectNotFound:
            flash("Venue not found")
            util.redirect("/")
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
            flash("Venue not found")
            util.redirect("/")
        if viewing == "no":
            util.redirect_previous()
        else:
            util.redirect("/venues/%s" % v.id)

    @expose("json", fragment=True)
    @identity.require(identity.not_anonymous())
    def dyntrack(self, id, track):
        u = identity.current.user
        ret = "Error"
        try:
            v = Venue.get(id)
            if track == "true" and v not in u.venues:
                u.addVenue(v)
                ret = "Tracked"
            if track == "false" and v in u.venues:
                u.removeVenue(v)
                ret = "Untracked"
        except SQLObjectNotFound:
            pass
        return ret

    @expose()
    @identity.require(identity.in_group("admin"))
    def merge(self, id, other_id):
        try:
            old = Venue.get(id)
            new = Venue.get(other_id)
            Venue.merge(old, new)
            # add this to fixup dict, so will never have to merge again
            venue_fixup_dict[old.name] = new.name
            flash("%s merged into %s and learned" % (old.name, new.name))
        except SQLObjectNotFound:
            flash("Could not move")
        util.redirect("/venues/%s" % other_id)

    @expose()
    @identity.require(identity.in_group("admin"))
    def delete(self, id):
        try:
            v = Venue.get(id)
            v.destroySelf()
            flash("Deleted")
        except SQLObjectNotFound:
            flash("Not Found")
        except SQLObjectIntegrityError:
            flash("Cannot delete")
        util.redirect("/venues/list")

