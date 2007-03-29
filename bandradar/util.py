import turbogears
import cherrypy
import formencode
from turbogears import identity
from turbogears import database
from sqlobject import SQLObjectNotFound, LIKE, func, AND

def dynsearch(model, name):
    result_cnt = 8
    def my_search(like_str):
        return model.select(
            AND(LIKE(func.LOWER(model.q.name), like_str), model.q.approved != None),
            orderBy=model.q.name)[:result_cnt]

    # check startswith first
    like_str = "%s%%" % unicode(name).lower()
    names = set([a.name for a in my_search(like_str)])
    if not len(names) > result_cnt / 2:
        # then go all out
        like_str = "%%%s%%" % unicode(name).lower()
        names = set([a.name for a in my_search(like_str)])
    return dict(results=list(names))

def search(model, name, tg_errors=None):
    if tg_errors:
        redirect_previous()

    name_str = "%s" % unicode(name).lower()
    result = model.select(
        AND(LIKE(func.LOWER(model.q.name), name_str), model.q.approved != None),
        orderBy=model.q.name)
    result_cnt = result.count()
    if not result_cnt:
        name_str = "%%%s%%" % unicode(name).lower()
        result = model.select(
            AND(LIKE(func.LOWER(model.q.name), name_str), model.q.approved != None),
            orderBy=model.q.name)
        result_cnt = result.count()

    if not result_cnt:
        turbogears.flash("Not Found")
        redirect_previous()
    elif result_cnt == 1:
        item = result[0]
        redirect("/%ss/%s" % (model.__name__.lower(), str(item.id)))
    else:
        return result

def redirect_previous():
    forward_url= cherrypy.request.headers.get("Referer", "/")

    # prevent redirect loops by going to main page
    if forward_url.endswith(cherrypy.request.path) or forward_url.endswith("login"):
        turbogears.redirect("/")
    else:
        turbogears.redirect(forward_url)

def redirect(where):
    turbogears.redirect(turbogears.url(where))

def can_edit(object):
    if 'admin' in identity.current.groups:
        return True
    if identity.current.user:
        return True
    return False

def can_delete(object):
    if 'admin' in identity.current.groups:
        return True
    return False

def desc_format(in_text):
    if not in_text:
        return ""
    import cgi
    out_text = cgi.escape(in_text)
    out_text = out_text.replace("\n", "<br />")
    return out_text

def so_to_dict(sqlobj):
    return database.so_to_dict(sqlobj)

class UniqueName(formencode.FancyValidator):

    def __init__(self, sqlmodel, **kwargs):
        super(UniqueName, self).__init__(**kwargs)
        self.model = sqlmodel

    def validate_python(self, field_dict, state):
        try:
            obj = self.model.byNameI(field_dict['name'])
            obj_id = field_dict['id']
            if obj.id != obj_id:
                turbogears.flash("Name already exists, now editing existing entry")                
                redirect("/%ss/%d/edit" % (obj.__class__.__name__.lower(), obj.id))
        except SQLObjectNotFound:
            pass

class RestAdapter:
    @turbogears.expose()
    def default(self, *vpath, **params):
        if not len(vpath):
            return self.list()
        elif len(vpath) == 1:
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
