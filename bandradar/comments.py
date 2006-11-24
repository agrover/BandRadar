import turbogears
from turbogears import controllers, expose, redirect
from turbogears import identity
from turbogears import widgets as w
from turbogears import validators as v

from elementtree import ElementTree

from model import Comment
import util

class CommentForm(w.WidgetsList):
    comment = w.TextArea(label="Comments?", rows=4, validator=v.NotEmpty(strip=True))

comment_form = w.TableForm(fields=CommentForm(), name="comment", submit_text="Send")

def get_by(row):
    if not row.comment_by:
        return "Anon"
    link = ElementTree.Element('a',href='mailto:%s' % row.comment_by.email_address)
    link.text = row.comment_by.user_name
    return link

datagrid = w.DataGrid(fields=[("Added", lambda row: row.created.strftime("%x")),
                              ("Comment", "comment"),
                              ("By", get_by)])

class Comments(controllers.Controller, util.RestAdapter):

    @expose(template=".templates.datagrid")
    def list(self):
        results = Comment.select(orderBy=Comment.q.created).reversed()
        return dict(title="hello", grid=datagrid, data=results)

    @expose(template=".templates.comment")
    def add(self):
        return dict(comment_form=comment_form)

    @expose()
    @turbogears.validate(form=comment_form)
    @turbogears.error_handler(add)
    def save(self, comment):
        c = Comment(comment=comment)
        if identity.current.user:
            c.comment_by = identity.current.user
        turbogears.flash("Comment saved, thanks!")
        util.redirect("/")