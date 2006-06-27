import turbogears
import cherrypy
from turbogears import identity
from turbogears import widgets as w
from turbogears import validators as v
from sqlobject import SQLObjectNotFound, LIKE, func, AND

def dynsearch(model, name):
    def my_search(like_str):
        result_cnt = 6
        return model.select(LIKE(func.LOWER(model.q.name), like_str),
            orderBy=model.q.name)[:result_cnt]

    # check startswith first
    like_str = "%s%%" % str(name).lower()
    names = [a.name for a in my_search(like_str)]
    if not len(names):
        # then go all out
        like_str = "%%%s%%" % str(name).lower()
        names = [a.name for a in my_search(like_str)]
    return dict(results=names)

def redirect_previous():
    forward_url= cherrypy.request.headers.get("Referer", "/")

    # prevent redirect loops by going to main page
    if forward_url.endswith(cherrypy.request.path) or forward_url.endswith("login"):
        turbogears.redirect("/")
    else:
        turbogears.redirect(forward_url)

def redirect(where):
    turbogears.redirect(turbogears.url(where))

def who_added():
    if "admin" in identity.current.groups:
        return None
    else:
        return identity.current.user

class BRAutoCompleteField(w.AutoCompleteField):
    def __init__(self, search_controller, label=""):
        super(w.AutoCompleteField, self).__init__(
            label=label,
            search_controller=search_controller,
            search_param="name",
            result_name="results",
            only_suggest=True,
            validator=v.Schema(text=v.NotEmpty(strip=True)),
            attrs={'size':20})

class RestAdapter:
    @turbogears.expose()
    def default(self, *vpath, **params):
        if len(vpath) == 1:
            identifier = vpath[0]
            action = self.show
        elif len(vpath) == 2:
            identifier, verb = vpath
            verb = verb.replace('.', '_')
            action = getattr(self, verb, None)
            if not action:
                raise cherrypy.NotFound
            if not action.exposed:
                raise cherrypy.NotFound
        else:
            raise cherrypy.NotFound
        return action(identifier, **params)
