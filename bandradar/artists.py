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
    id = w.HiddenField()
    name = w.TextField(validator=v.NotEmpty)
    desc = w.TextArea(label="Description")
    url = w.TextField(label="Website", attrs={'size':90},
        validator=v.Any(v.URL, v.Empty))

artist_form = w.TableForm(fields=ArtistForm(), name="artist", submit_text="Save")

class SearchBox(w.WidgetsList):
    search = w.AutoCompleteField(label="",
        search_controller="/artists/dynsearch",
        search_param="name",
        result_name="results",
        only_suggest=True,
        validator=v.Schema(text=v.NotEmpty(strip=True)),
        attrs={'size':20})

artist_search_form = w.ListForm(fields=SearchBox(), name="search",
    submit_text="Search")


class Artists(controllers.Controller, util.RestAdapter):

    @expose(allow_json=True)
    def dynsearch(self, name):
        def my_search(like_str):
            result_cnt = 6
            return Artist.select(LIKE(func.LOWER(Artist.q.name), like_str),
                orderBy=Artist.q.name)[:result_cnt]

        # check startswith first
        like_str = "%s%%" % str(name).lower()
        names = [a.name for a in my_search(like_str)]
        if not len(names):
            # then go all out
            like_str = "%%%s%%" % str(name).lower()
            names = [a.name for a in my_search(like_str)]
        return dict(results=names)

    @expose()
    @turbogears.validate(form=artist_search_form)
    def search(self, search, tg_errors=None):
        if tg_errors:
            redirect("/")
        try:
            a = Artist.byName(search['text'])
            redirect("/artists/%s" % str(a.id))
        except SQLObjectNotFound:
            redirect("/artists/new?name=%s" % search['text'])

    @expose(template=".templates.artistlist")
    def list(self, listby="today", orderby="alpha"):

        def listday(day_delta):
            day_result = []
            events = Event.select(Event.q.date == date.today()-timedelta(day_delta))
            for event in events:
                for artist in event.artists:
                    art = dict(id=artist.id, name=artist.name)
                    if identity.current.user:
                        art['is_tracked'] = artist in identity.current.user.artists
                    else:
                        art['is_tracked'] = False
                    day_result.append(art)
            return day_result

        if listby == "all":
            result = []
            artists = Artist.select(AND(Artist.q.verified == True,
                Artist.q.active == True), orderBy=Artist.q.name)
            for artist in artists:
                art = dict(id=artist.id, name=artist.name)
                if identity.current.user:
                    art['is_tracked'] = artist in identity.current.user.artists
                else:
                    art['is_tracked'] = False
                result.append(art)
        elif listby == "yesterday":
            result = listday(-1)
        elif listby == "today":
            result = listday(0)
        elif listby == "tomorrow":
            result = listday(1)
        elif listby == "top":
            result = []

        # order by alpha, pop, date

        return dict(artists=result)

    @expose(template=".templates.artistshow")
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
        return dict(artist=a, events=a.events, is_tracked=is_tracked)

    @expose(template=".templates.artistedit")
    @identity.require(identity.not_anonymous())
    def new(self, name=""):
        form_vals = dict(name=name)
        return dict(artist_form=artist_form, form_vals=form_vals)

    @expose(template=".templates.artistedit")
    @identity.require(identity.not_anonymous())
    def edit(self, id=0, **kw):
        form_vals = {}
        if id:
            try:
                a = Artist.get(id)
                form_vals = dict(id=id, name=a.name, desc=a.description, url=a.url)
            except SQLObjectNotFound:
                pass
        form_vals.update(kw)
        return dict(artist_form=artist_form, form_vals=form_vals)

    @expose()
    @identity.require(identity.not_anonymous())
    @turbogears.validate(form=artist_form)
    @turbogears.error_handler(edit)
    def save(self, name, id=0, desc="", url=""):
        hub.begin()
        if id:
            try:
                a = Artist.get(id)
                a.name = name
                a.description = desc
                a.url = url
                turbogears.flash("Updated")
            except SQLObjectNotFound:
                turbogears.flash("Update Error")
        else:
            a = Artist(name=name, description=desc, url=url, added_by=util.who_added())
            if not "admin" in identity.current.groups:
                identity.current.user.addArtist(a)
            turbogears.flash("Added")
        hub.commit()
        redirect(turbogears.url("/artists/%s" % a.id))

    @expose()
    @identity.require(identity.not_anonymous())
    def track(self, id, viewing="no"):
        hub.begin()
        u = identity.current.user
        try:
            a = Artist.get(id)
            if a not in u.artists:
                u.addArtist(a)
        except SQLObjectNotFound:
            turbogears.flash("Artist not found")
            redirect("/")
        hub.commit()
        if viewing == "no":
            util.redirect_previous()
        else:
            util.redirect("/artists/%s" % a.id)

    @expose()
    @identity.require(identity.not_anonymous())
    def untrack(self, id, viewing="no"):
        hub.begin()
        u = identity.current.user
        try:
            a = Artist.get(id)
            if a in u.artists:
                u.removeArtist(a)
        except SQLObjectNotFound:
            turbogears.flash("Artist not found")
            redirect("/")
        hub.commit()
        if viewing == "no":
            util.redirect_previous()
        else:
            util.redirect("/artists/%s" % a.id)

    @expose()
    @identity.require(identity.in_group("admin"))
    def delete(self, id):
        hub.begin()
        try:
            a = Artist.get(id)
            for e in a.events:
                a.removeEvent(e)
            e.destroySelf()
            turbogears.flash("Deleted")
        except SQLObjectNotFound:
            turbogears.flash("Delete failed")
        hub.commit()
        redirect(turbogears.url("/artists/list"))
