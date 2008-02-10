from turbogears import controllers, expose, validate, error_handler, flash
from turbogears import identity
from turbogears import widgets as w
from turbogears import validators as v

from model import Artist, Event, hub
from sqlobject import SQLObjectNotFound, LIKE, func, AND
from datetime import date, datetime, timedelta
import urllib
import util
from importers import artist_fixup_dict
from widgets import BRAutoCompleteField, artist_list

class ArtistForm(w.WidgetsList):
    id = w.HiddenField(validator=v.Int)
    name = w.TextField(attrs=dict(size=40),
        validator=v.All(v.NotEmpty(strip=True),v.UnicodeString()))
    description = w.TextArea(label="Description", rows=4,
        validator=v.UnicodeString(strip=True))
    url = w.TextField(label="Website", attrs=dict(size=40),
        validator=v.Any(v.URL, v.Empty))
    myspace = w.TextField(label="MySpace", attrs=dict(maxlength=40),
        help_text="either myspace.com/abc or abc")
    is_dj = w.CheckBox(label="Is a DJ", default=False)

class ArtistSchema(v.Schema):
    chained_validators = [util.UniqueName(Artist)]

artist_form = w.TableForm(fields=ArtistForm(), name="artist", submit_text="Save",
                            validator=ArtistSchema())

class ArtistController(controllers.Controller, util.RestAdapter):

    @expose(template=".templates.artist.list")
    def list(self, listby="today", orderby="alpha"):

        def artists_with_shows(day_delta, day_count=1):
            conn = hub.getConnection()

            start_date = date.today() + timedelta(day_delta)
            where_clause = AND(Event.q.date >= start_date, Event.q.approved != None)
            if day_count != 0:
                end_date = start_date + timedelta(day_count-1)
                where_clause = AND(where_clause, Event.q.date <= end_date)

            artists = conn.queryAll("""
                select artist.id, artist.name, venue.name
                from artist, event, artist_event, venue
                where artist.id = artist_event.artist_id and
                    artist_event.event_id = event.id and 
                    venue.id = event.venue_id and
                    %s
                order by artist.name
                """ % where_clause)

            day_result = {}
            if identity.current.user:
                tracked_artist_ids = [a.id for a in identity.current.user.artists]
            else:
                tracked_artist_ids = []
            for artist_id, artist_name, venue_name in artists:
                is_tracked = artist_id in tracked_artist_ids
                day_result[artist_name] = (artist_id, is_tracked, venue_name)
            return day_result

        if listby == "today":
            result = artists_with_shows(0)
        elif listby == "tomorrow":
            result = artists_with_shows(1)
        elif listby == "yesterday":
            result = artists_with_shows(-1)
        elif listby == "week":
            result = artists_with_shows(0, 7)
        elif listby == "all":
            result = artists_with_shows(0, 0)
        else:
            result = {}

        # we stored items in a dict to uniquify artist names.
        # now, sort and put back in a list
        keys = result.keys()
        keys.sort()
        result_list = [dict(name=key, id=result[key][0], is_tracked=result[key][1], 
            venue_name=result[key][2]) for key in keys]

        return dict(artists=result_list, count=len(result), listby=listby)

    @expose(template=".templates.artist.show")
    def show(self, id, list_all=0):
        try:
            a = Artist.get(id)
        except SQLObjectNotFound:
            flash("Artist ID not found")
            util.redirect("/artists/list")
        except ValueError:
            try:
                a = Artist.byNameI(urllib.unquote_plus(id))
            except SQLObjectNotFound:
                flash("Artist ID not found")
                util.redirect("/artists/list")

        if identity.current.user and a in identity.current.user.artists:
            is_tracked = True
        else:
            is_tracked = False

        past_events = a.events.filter(Event.q.date < date.today()).orderBy('-date')
        if not list_all:
            past_events = past_events[:5]
        future_events = a.events.filter(Event.q.date >= date.today()).orderBy('date')
        return dict(artist=a, past_events=past_events, future_events=future_events,
            tracked_count=a.users.count(), is_tracked=is_tracked,
            description=util.desc_format(a.description), artist_list=artist_list)

    @expose(template=".templates.artist.edit")
    @identity.require(identity.not_anonymous())
    def edit(self, id=0, **kw):
        form_vals = {}
        if id:
            try:
                a = Artist.get(id)
                form_vals = util.so_to_dict(a)
            except SQLObjectNotFound:
                pass
        form_vals.update(kw)
        return dict(artist_form=artist_form, form_vals=form_vals)

    @expose()
    @identity.require(identity.not_anonymous())
    @validate(form=artist_form)
    @error_handler(edit)
    def save(self, id=0, **kw):
        if id:
            try:
                a = Artist.get(id)
                a.set(**a.clean_dict(kw))
                flash("Updated")
            except SQLObjectNotFound:
                flash("Update Error")
        else:
            a = Artist(added_by=identity.current.user, **Artist.clean_dict(kw))
            if not "admin" in identity.current.groups:
                identity.current.user.addArtist(a)
            flash("Artist added")
        a.approved = datetime.now()
        util.redirect("/artists/%s" % a.id)

    @expose()
    @identity.require(identity.not_anonymous())
    def track(self, id, viewing="no"):
        u = identity.current.user
        try:
            a = Artist.get(id)
            if a not in u.artists:
                u.addArtist(a)
        except SQLObjectNotFound:
            flash("Artist not found")
            redirect("/")
        if viewing == "no":
            util.redirect_previous()
        else:
            util.redirect("/artists/%s" % a.id)

    @expose()
    @identity.require(identity.not_anonymous())
    def untrack(self, id, viewing="no"):
        u = identity.current.user
        try:
            a = Artist.get(id)
            if a in u.artists:
                u.removeArtist(a)
        except SQLObjectNotFound:
            flash("Artist not found")
            util.redirect("/")
        if viewing == "no":
            util.redirect_previous()
        else:
            util.redirect("/artists/%s" % a.id)

    @expose("json", fragment=True)
    @identity.require(identity.not_anonymous())
    def dyntrack(self, id, track):
        u = identity.current.user
        ret = "Error"
        try:
            a = Artist.get(id)
            if track == "true" and a not in u.artists:
                u.addArtist(a)
                ret = "Tracked"
            if track == "false" and a in u.artists:
                u.removeArtist(a)
                ret = "Untracked"
        except SQLObjectNotFound:
            pass
        return ret

    @expose()
    @identity.require(identity.in_group("admin"))
    def split(self, id):
        try:
            a = Artist.get(id)
            new_artists = a.split_artist()
            if len(new_artists) > 1:
                flash("split into %s" % ", ".join(new_artists.values()))
            else:
                flash("Not split")
        except SQLObjectNotFound:
            flash("not found")
        util.redirect("/artists/%s" % new_artists.keys()[0])

    @expose()
    @identity.require(identity.in_group("admin"))
    def merge(self, id, other_id):
        try:
            old = Artist.get(id)
            new = Artist.get(other_id)
            Artist.merge(old, new)
            # add this to fixup dict, so will never have to merge again
            artist_fixup_dict[old.name] = new.name
            artist_fixup_dict.tidy(old.name, new.name)
            flash("%s merged into %s and learned" % (old.name, new.name))
        except SQLObjectNotFound:
            flash("Could not move")
        util.redirect("/artists/%s" % other_id)

    @expose()
    @identity.require(identity.in_group("admin"))
    def delete(self, id):
        try:
            a = Artist.get(id)
            a.destroySelf()
            flash("Deleted")
        except SQLObjectNotFound:
            flash("Delete failed")
        util.redirect("/artists/list")

