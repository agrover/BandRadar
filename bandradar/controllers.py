import logging
import cherrypy
import turbogears
from turbogears import controllers, expose, redirect
from turbogears import identity
from turbogears import scheduler
from turbogears import widgets as w
from turbogears import validators as v
from turbogears import paginate
from turbogears.view import root_variable_providers
from sqlobject import AND, NOT, IN, SQLObjectNotFound

from artists import Artists, artist_search_form
from venues import Venues
from events import Events
from users import Users
from importers import Importers
from comments import Comments
from model import Event, UpdateLog, UserAcct, BatchRecord, Group, hub
import batch
import saved_visit
import util

import datetime

from xml.etree import ElementTree

log = logging.getLogger("bandradar.controllers")

# ---------- Startup ----------

def add_root_vars(root_dict):
    pass

def br_startup():
    #scheduler.add_interval_task(batch.task, 60)
    scheduler.add_weekday_task(batch.task, range(1,8), (3,0))
    saved_visit.start_extension()
    root_variable_providers.append(add_root_vars)

def br_shutdown():
    saved_visit.shutdown_extension()

turbogears.startup.call_on_startup.append(br_startup)
turbogears.startup.call_on_shutdown.append(br_shutdown)

# ---------- Datagrids ----------

def get_by(row):
    if row.table_name == "artist_event":
        try:
            e = Event.get(row.table_id)
            link = ElementTree.Element('a', href='/events/%d' % e.id)
            link.text = str(e.id)
        except SQLObjectNotFound:
            return "none"
    else:
        link = ElementTree.Element('a', href='/%ss/%d' % (row.table_name, row.table_id))
        link.text = str(row.table_id)
    return link

def changed_by(row):
    if not row.changed_by:
        return "Nobody (batch)"
    else:
        return UserAcct.get(row.changed_by).user_name

udl_datagrid = w.PaginateDataGrid(fields=[
                w.DataGrid.Column("created",
                    lambda row: row.created.strftime("%x %X"),
                    options=dict(sortable=True)),
                w.DataGrid.Column("changed_by", changed_by,
                    title="By", options=dict(sortable=True)),
                w.DataGrid.Column("table_name", title="Table",
                    options=dict(sortable=True)),
                w.DataGrid.Column("table_id", get_by, options=dict(sortable=True)),
                w.DataGrid.Column("attrib_name", title="Prop"),
                w.DataGrid.Column("old", lambda row: unicode(row.attrib_old_value)),
                w.DataGrid.Column("new", lambda row: unicode(row.attrib_new_value)),
                ])

def batch_time(row):
    if not row.finished:
        return "running"
    else:
        return row.finished - row.started

br_datagrid = w.PaginateDataGrid(fields=[
                ("Started", "started"),
                w.DataGrid.Column("Time", batch_time),
                ("Email sent", "email_sent"),
                ("Events Pinged", "artist_pings"),
                ("Venues Pinged", "venue_pings"),
                ("Sims Updated", "sims_updated"),
                ("Recs Updated", "recordings_updated"),
                ("Geocodes Updated", "geocodes_updated"),
                ])

# ---------- Controller ----------

class Root(controllers.RootController):

    @expose(template=".templates.main")
    def index(self):
        conn = hub.getConnection()

        events = conn.queryAll("""
            select event.id, event.name, venue.name
            from event, venue
            where event.venue_id = venue.id
                and event.date = CURRENT_DATE
                and event.approved is not NULL
            order by venue.name
            """)

        top_artists = conn.queryAll("""
            select a.name, a.id, COUNT(aua.user_acct_id) as count
            from artist a, artist_user_acct aua
            where a.id = aua.artist_id
            group by a.name, a.id
            order by count desc, name
            limit 10
            """)
        top_artists = [dict(name=a, id=b, count=c) for a, b, c in top_artists]

        top_venues = conn.queryAll("""
            select v.name, v.id, COUNT(uav.user_acct_id) as count
            from venue v, user_acct_venue uav
            where v.id = uav.venue_id
            group by v.name, v.id
            order by count desc, name
            limit 10
            """)
        top_venues = [dict(name=a, id=b, count=c) for a, b, c in top_venues]

        top_events = conn.queryAll("""
            select e.name, e.id, COUNT(att.user_id) as count
            from event e, attendance att
            where e.id = att.event_id
                and e.date >= CURRENT_DATE
            group by e.name, e.id
            order by count desc, name
            limit 10
            """)
        top_events = [dict(name=a, id=b, count=c) for a, b, c in top_events]

        return dict(search_form=artist_search_form, events=events,
            top_artists=top_artists, top_venues=top_venues, top_events=top_events)

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

    @expose(template=".templates.faq")
    def faq(self):
        return dict()

    @expose(template=".templates.contact")
    def contact(self):
        return dict()

    @expose(template=".templates.notimplemented")
    def feeds(self):
        return dict()

    @expose(template=".templates.nearestvenues")
    def nearestvenues(self, location):
        pass

    @expose(template=".templates.datagrid")
    @identity.require(identity.in_group("admin"))
    @paginate("data", default_order="created", limit=25)
    def list_update_log(self, filter_admin=1):
        results = UpdateLog.select().reversed()
        if filter_admin:
            g = Group.by_group_name("admin")
            results = results.filter(NOT(IN(UpdateLog.q.changed_by, [u.id for u in g.users])))
        return dict(title="BandRadar Update Log", grid=udl_datagrid, data=results)

    @expose(template=".templates.datagrid")
    @identity.require(identity.in_group("admin"))
    @paginate("data", default_order="started", limit=25)
    def list_batch(self):
        results = BatchRecord.select().reversed()
        return dict(title="BandRadar Batch Stats", grid=br_datagrid, data=results)
