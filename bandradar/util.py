import logging
import turbogears
import cherrypy
from formencode import FancyValidator
from turbogears import identity
from turbogears import database
from turbogears import config
from sqlobject import SQLObjectNotFound, LIKE, func, AND
from bandradar.imports import import_util

log = logging.getLogger("bandradar.util")

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
    return list(names)

def dynmultisearch(models, name):
    results = []
    for model in models:
        x = dynsearch(model, name)
        results.extend(x)
    return dict(results=results)

def search(model, name, limit=100, tg_errors=None):
    if tg_errors:
        redirect_previous()

    name_str = "%s" % unicode(name).lower()
    result = model.select(
        AND(LIKE(func.LOWER(model.q.name), name_str), model.q.approved != None),
        orderBy=model.q.name)[:limit]
    result_cnt = result.count()
    if not result_cnt:
        name_str = "%%%s%%" % unicode(name).lower()
        result = model.select(
            AND(LIKE(func.LOWER(model.q.name), name_str), model.q.approved != None),
            orderBy=model.q.name)[:limit]
    return result

def is_production():
    if config.get("server.environment", "development") == "development":
        return False
    else:
        return True


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
    out_text = import_util.escape(in_text)
    out_text = out_text.replace("\n", "<br />")
    return out_text

def so_to_dict(sqlobj):
    return database.so_to_dict(sqlobj)

def clean_dict(cls, dirty_dict):
    """ensure the dict only has keys that are columns in the given sqlobject class"""
    clean = dict()
    valid_attributes = cls.sqlmeta.columns.keys()
    for attr, value in dirty_dict.iteritems():
        if attr in valid_attributes:
            if isinstance(value, basestring):
                value = value.strip()
            if attr == "myspace" and value:
                value = value.split("/")[-1]
            clean[attr] = value
    return clean


class UniqueName(FancyValidator):

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

#
# A database-backed dict.
#
class PersistentDict(dict):
    def __init__(self, model):
        super(PersistentDict, self).__init__()
        self.model = model
        for row in model.select():
            super(PersistentDict, self).__setitem__(row.name, row.value)

    def __setitem__(self, name, value):
        try:
            r = self.model.byName(name)
            r.value = value
        except SQLObjectNotFound:
            r = self.model(name=name, value=value)
        super(PersistentDict, self).__setitem__(name, value)

    def __delitem__(self, name):
        self.model.byName(name).destroySelf()
        super(PersistentDict, self).__delitem__(name)

    def update(self, other_dict):
        for name, value in other_dict.iteritems():
            try:
                r = self.model.byName(name)
                r.value = value
            except SQLObjectNotFound:
                r = self.model(name=name, value=value)
        super(PersistentDict, self).update(other_dict)

    def pop (self, item, *default):
        key = self.has_key(item)
        if key == False:
            if len(default) != 1:
                raise KeyError(item)
            else:
                return default[0]
        val = self[item]
        del self[item]
        return val

    # specific to our usage of this class (fixup table)
    def tidy(self, old_name, new_name):
        self.pop(new_name, None)
        for name, value in self.iteritems():
            if value == old_name:
                self[name] = new_name

    def find_cycles(self):
        for name, value in self.iteritems():
            if self.has_key(value):
                print name, "->", value, "->", self[value]

def email(msg_to, msg_from, subject, body):
    import smtplib
    from email.MIMEText import MIMEText
    from email.Utils import make_msgid, formatdate

    if not is_production():
        msg_to = "andy@groveronline.com"

    msg = MIMEText(body.encode('utf8'), 'plain', 'utf8')
    msg['To'] = msg_to
    msg['From'] = msg_from
    msg['Subject'] = subject
    msg['Date'] = formatdate(localtime=True)
    msg['Message-ID'] = make_msgid()

    s = smtplib.SMTP()
    s.connect()
    try:
        s.sendmail(msg_from, [msg_to], msg.as_string())
    except smtplib.SMTPException, smtp:
        # todo: record bounces so a human can do something
        log.error("smtp error %s" % repr(smtp))
    s.close()

