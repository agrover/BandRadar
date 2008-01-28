from turbogears import controllers, expose, validate, error_handler, paginate, flash
from turbogears import identity
from turbogears import widgets as w
from turbogears import validators as v
from sqlobject import SQLObjectNotFound

from xml.etree import ElementTree
from docutils.core import publish_parts

from model import Blurb
from widgets import BRCalendarDatePicker, ButtonWidget

import util

class BlurbForm(w.WidgetsList):
    id = w.HiddenField(validator=v.Int)
    text = w.TextArea(label="Blurb", rows=4,
        validator=v.All(v.NotEmpty(strip=True),v.UnicodeString()))
    expiry = BRCalendarDatePicker(not_empty=False)
    preview = w.SubmitButton(label="", attrs=dict(value="Preview"))

blurb_form = w.TableForm(fields=BlurbForm(), name="blurb", submit_text="Save")

def get_by(row):
    link = ElementTree.Element('a',href='mailto:%s' % row.added_by.email_address)
    link.text = row.added_by.user_name
    return link

def get_text(row):
    text = publish_parts(row.text, writer_name="html")["html_body"]
    return ElementTree.fromstring(text)

widget = ButtonWidget()

def get_actions(row):
    div = ElementTree.Element("div")
    div.append(widget.display(action="/blurbs/edit/%s" % row.id, label="Edit"))
    div.append(widget.display(action="/blurbs/delete/%s" % row.id, label="Delete"))
    return div

datagrid = w.PaginateDataGrid(fields=(
                w.DataGrid.Column("created", lambda row: row.created.strftime("%x"),
                    options=dict(sortable=True)),
                w.DataGrid.Column("By", get_by, options=dict(sortable=True)),
                w.DataGrid.Column("expires",
                    lambda row: row.expiry.strftime("%x") if row.expiry else "Never",
                    options=dict(sortable=True)),
                w.DataGrid.Column("text", get_text, options=dict(sortable=True)),
                w.DataGrid.Column("Actions", get_actions),
                )
            )

class BlurbController(controllers.Controller, identity.SecureResource):
    require = identity.in_group("admin")

    @expose(template=".templates.blurb.list")
    @paginate("data", default_order="created")
    def list(self):
        results = Blurb.select().reversed()
        return dict(title="Blurbs", grid=datagrid, data=results)

    @expose(template=".templates.blurb.edit")
    def edit(self, id=0, **kw):
        form_vals = {}
        if id:
            try:
                b = Blurb.get(id)
                form_vals = util.so_to_dict(b)
            except SQLObjectNotFound:
                pass
        form_vals.update(kw)
        return dict(blurb_form=blurb_form, form_vals=form_vals, blurb=None)

    @expose()
    @validate(form=blurb_form)
    @error_handler(edit)
    def save(self, id, **kw):
        if id:
            try:
                b = Blurb.get(id)
                b.set(**util.clean_dict(Blurb, kw))
                flash("Updated")
            except SQLObjectNotFound:
                flash("Update Error")
        else:
            if kw.get("preview"):
                kw['show_text'] = publish_parts(kw['text'], writer_name="html")["html_body"]
                return self.edit(**kw)
            else:
                b = Blurb(added_by=identity.current.user, **util.clean_dict(Blurb, kw))
                flash("Blurb added")
        util.redirect("/blurbs/list")

    @expose()
    def delete(self, id):
        try:
            b = Blurb.get(id)
            b.destroySelf()
            flash("Deleted")
        except SQLObjectNotFound:
            flash("Delete failed")
        util.redirect("/blurbs/list")

