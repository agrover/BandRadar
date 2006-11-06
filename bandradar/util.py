import turbogears
import cherrypy
import formencode
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
    names = set([a.name for a in my_search(like_str)])
    if not len(names):
        # then go all out
        like_str = "%%%s%%" % str(name).lower()
        names = set([a.name for a in my_search(like_str)])
    return dict(results=list(names))

def search(model, name, tg_errors=None):
    if tg_errors:
        redirect_previous()

    name_str = "%s%%" % str(name).lower()
    result = model.select(LIKE(func.LOWER(model.q.name), name_str),
        orderBy=model.q.name)
    result_cnt = result.count()
    if not result_cnt:
        name_str = "%%%s%%" % str(name).lower()
        result = model.select(LIKE(func.LOWER(model.q.name), name_str),
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
    if object.added_by == identity.current.user:
        return True
    return False

def can_delete(object):
    if 'admin' in identity.current.groups:
        return True
    return False

class UniqueName(formencode.FancyValidator):

    def __init__(self, sqlmodel):
        self.model = sqlmodel

    def validate_python(self, value, state):
        rows = self.model.select(func.LOWER(self.model.q.name) == unicode.lower(value)).count()
        if rows:
            raise formencode.Invalid('Sorry, that name exists', value, state)


class ButtonWidget(w.Widget):
    params=['label', 'action']

    template = '''
    <form xmlns:py="http://purl.org/kid/ns#"
        class="buttonform"
        action="${action}"
        method="POST">
        <input class="button" type="submit" value="${label}"/>
    </form>
    '''

class AutoCompleteValidator(v.Schema):
    def _to_python(self, value, state):
        text = value['text']
        value['text'] = v.NotEmpty(strip=True).to_python(text)
        return value

class BRAutoCompleteField(w.AutoCompleteField):
    def __init__(self, search_controller, label=""):
        super(w.AutoCompleteField, self).__init__(
            label=label,
            search_controller=search_controller,
            search_param="name",
            result_name="results",
            only_suggest=True,
            validator=AutoCompleteValidator(),
            attrs=dict(size=20))

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
