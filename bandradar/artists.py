import turbogears
from turbogears import controllers, expose, redirect
from turbogears import identity
from turbogears import widgets as w
from turbogears import validators as v

from model import Artist, Event, hub
from sqlobject import SQLObjectNotFound, LIKE, func, AND
from datetime import date, timedelta
import util

class ArtistForm(w.WidgetsList):
    id = w.HiddenField(validator=v.Int)
    name = w.TextField(validator=v.NotEmpty(strip=True))
    description = w.TextArea(label="Description", rows=4)
    url = w.TextField(label="Website", attrs=dict(size=60),
        validator=v.Any(v.URL, v.Empty))
    myspace = w.TextField(label="MySpace", attrs=dict(maxlength=40),
        help_text="e.g. myspace.com/abc, enter abc")

class ArtistSchema(v.Schema):
    chained_validators = [util.UniqueName(Artist)]

artist_form = w.TableForm(fields=ArtistForm(), name="artist", submit_text="Save",
                            validator=ArtistSchema())

class SearchBox(w.WidgetsList):
    search = util.BRAutoCompleteField("/artists/dynsearch")

artist_search_form = w.ListForm(fields=SearchBox(), name="search",
    submit_text="Search")


class Artists(controllers.Controller, util.RestAdapter):

    @expose(allow_json=True)
    def dynsearch(self, name):
        return util.dynsearch(Artist, name)

    @expose(template=".templates.artist.search_results")
    @turbogears.validate(form=artist_search_form)
    def search(self, search, tg_errors=None):
        results = util.search(Artist, search['text'], tg_errors)
        return dict(artists=results, artist_search_form=artist_search_form)

    @expose(template=".templates.artist.list")
    def list(self, listby="today", orderby="alpha"):

        def artists_with_shows(day_delta, day_count=1):
            day_result = {}
            start_date = date.today() + timedelta(day_delta)
            where_clause = AND(Event.q.date >= start_date, Event.q.approved != None)
            if day_count != 0:
                end_date = start_date + timedelta(day_count-1)
                where_clause = AND(where_clause, Event.q.date <= end_date)
            events = Event.select(where_clause)
            for event in events:
                for artist in event.artists:
                    if identity.current.user:
                        is_tracked = artist in identity.current.user.artists
                    else:
                        is_tracked = False
                    art = dict(id=artist.id, name=artist.name)
                    day_result[artist.name] = (artist.id, is_tracked)
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
        result_list = [dict(name=key, id=result[key][0], is_tracked=result[key][1])
            for key in keys]

        return dict(artists=result_list, count=len(result),
            listby=listby, artist_search_form=artist_search_form)

    @expose(template=".templates.artist.show")
    def show(self, id):
        try:
            a = Artist.get(id)
            if identity.current.user and a in identity.current.user.artists:
                is_tracked = True
            else:
                is_tracked = False
        except SQLObjectNotFound:
            turbogears.flash("Artist ID not found")
            redirect(turbogears.url("/artists/list"))

        past_events = a.events.filter(Event.q.date < date.today()).orderBy(Event.q.date).reversed()[:5]
        past_events = list(reversed(list(past_events)))
        future_events = a.events.filter(Event.q.date >= date.today()).orderBy(Event.q.date)
        return dict(artist=a, past_events=past_events, future_events=future_events,
            tracked_count=a.users.count(), is_tracked=is_tracked,
            description=util.desc_format(a.description))

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
    @turbogears.validate(form=artist_form)
    @turbogears.error_handler(edit)
    def save(self, id=0, **kw):
        if id:
            try:
                a = Artist.get(id)
                a.set(**a.clean_dict(kw))
                turbogears.flash("Updated")
            except SQLObjectNotFound:
                turbogears.flash("Update Error")
        else:
            a = Artist(added_by=identity.current.user, **Artist.clean_dict(kw))
            if not "admin" in identity.current.groups:
                identity.current.user.addArtist(a)
            turbogears.flash("Artist added")
        redirect(turbogears.url("/artists/%s" % a.id))

    @expose()
    @identity.require(identity.not_anonymous())
    def track(self, id, viewing="no"):
        u = identity.current.user
        try:
            a = Artist.get(id)
            if a not in u.artists:
                u.addArtist(a)
        except SQLObjectNotFound:
            turbogears.flash("Artist not found")
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
            turbogears.flash("Artist not found")
            redirect("/")
        if viewing == "no":
            util.redirect_previous()
        else:
            util.redirect("/artists/%s" % a.id)


    @expose()
    @identity.require(identity.in_group("admin"))
    def delete(self, id):
        try:
            a = Artist.get(id)
            a.destroySelf()
            turbogears.flash("Deleted")
        except SQLObjectNotFound:
            turbogears.flash("Delete failed")
        redirect(turbogears.url("/artists/list"))
