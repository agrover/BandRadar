import logging
import cherrypy
import turbogears
from turbogears import controllers, expose, redirect
from turbogears import identity
from turbogears import scheduler
from turbogears import widgets as w
from turbogears import validators as v
from turbogears import paginate
from sqlobject import AND

from artists import Artists, artist_search_form
from venues import Venues
from events import Events
from users import Users
from importers import Importers
from comments import Comments
from model import Event, UpdateLog, UserAcct, BatchRecord, hub
import batch
import saved_visit
import util

import datetime

from elementtree import ElementTree
import pickle

log = logging.getLogger("bandradar.controllers")


def br_startup():
    #scheduler.add_interval_task(batch.task, 60)
    scheduler.add_weekday_task(batch.task, range(1,8), (3,0))
    saved_visit.start_extension()

def br_shutdown():
    saved_visit.shutdown_extension()

turbogears.startup.call_on_startup.append(br_startup)
turbogears.startup.call_on_shutdown.append(br_shutdown)

def get_by(row):
    link = ElementTree.Element('a',href='/%ss/%d' % (row.table_name, row.table_id))
    link.text = str(row.table_id)
    return link

udl_datagrid = w.PaginateDataGrid(fields=[
                w.DataGrid.Column("created",
                    lambda row: row.created.strftime("%x %X"),
                    options=dict(sortable=True)),
                w.DataGrid.Column("changed_by",
                    lambda row: UserAcct.get(row.changed_by).user_name,
                    title="By", options=dict(sortable=True)),
                w.DataGrid.Column("table_name", title="Table",
                    options=dict(sortable=True)),
                w.DataGrid.Column("table_id", get_by, options=dict(sortable=True)),
                w.DataGrid.Column("attrib_name", title="Prop"),
                w.DataGrid.Column("old", lambda row: str(pickle.loads(str(row.attrib_old_value)))),
                w.DataGrid.Column("new", lambda row: str(pickle.loads(str(row.attrib_new_value)))),
                ])

br_datagrid = w.PaginateDataGrid(fields=[
                ("Started", "started"),
                w.DataGrid.Column("Time", lambda row: row.finished - row.started),
                ("Email sent", "email_sent"),
                ])

class Root(controllers.RootController):

    @expose(template=".templates.main")
    def index(self):
        if identity.current.user:
            user = identity.current.user.user_name
        else:
            user = "unknown person"

        events = Event.select(AND(Event.q.date == datetime.date.today(),
            Event.q.approved != None),
            orderBy=Event.q.name)#[:10]

        conn = hub.getConnection()
        top_tracked_results = conn.queryAll("""
            select artist.name, artist.id, COUNT(artist_user_acct.user_acct_id) as count
            from artist
            left join artist_user_acct on artist.id = artist_user_acct.artist_id
            group by artist.name, artist.id
            order by count desc, name
            limit 20
            """)

        top_tracked = []
        for name, id, count in top_tracked_results:
            top_tracked.append(dict(name=name, id=id, count=count))

        return dict(user=user, search_form=artist_search_form, events=events,
            top_tracked=top_tracked)

    artists = Artists()
    venues = Venues()
    events = Events()
    users = Users()
    importers = Importers()
    comments = Comments()

    @expose(template=".templates.output")
    def test(self):
        return dict(output="hello")
        #return dict(output=str(identity.current_provider))

    @expose(template=".templates.about")
    def about(self):
        return dict()

    @expose(template=".templates.privacy")
    def privacy(self):
        return dict()

    @expose(template=".templates.notimplemented")
    def contact(self):
        return dict()

    @expose(template=".templates.notimplemented")
    def feeds(self):
        return dict()

    @expose(template=".templates.datagrid")
    @identity.require(identity.in_group("admin"))
    @paginate("data", default_order="created", limit=25)
    def list_update_log(self, filter_user=None):
        results = UpdateLog.select().reversed()
        if filter_user:
            results = results.filter(UpdateLog.q.changed_by == int(filter_user))
        return dict(title="BandRadar Update Log", grid=udl_datagrid, data=results)

    @expose(template=".templates.datagrid")
    @identity.require(identity.in_group("admin"))
    @paginate("data", default_order="started", limit=25)
    def list_batch(self):
        results = BatchRecord.select().reversed()
        return dict(title="BandRadar Batch Stats", grid=br_datagrid, data=results)
