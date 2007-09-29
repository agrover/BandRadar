from datetime import datetime, date, timedelta

from sqlobject import *
from sqlobject.joins import SORelatedJoin, SOMultipleJoin
from sqlobject.events import listen, RowUpdateSignal
from turbogears.database import PackageHub
from turbogears import identity

import pickle

hub = PackageHub("bandradar")
__connection__ = hub

soClasses = ('UserAcct', 'Group', 'Permission', 'Venue', 'Artist',
             'SimilarArtist', 'Event', 'BatchRecord', 'Attendance',
             'Comment', 'UpdateLog', 'Source', 'Recording',
             'ArtistNameFixup', 'VenueNameFixup')

def fancy_date(past_date):
    """Take a date in the past and return it pretty-printed, with elapsed time.

    """
    elapsed = datetime.now() - past_date
    if elapsed.days > 1:
        return "%s (%d days ago)" % (past_date.strftime("%x"), elapsed.days)
    if elapsed.days == 1:
        return "%s (%d day ago)" % (past_date.strftime("%x"), elapsed.days)
    if elapsed.seconds / 7200:
        return "%s (%d hours ago)" % (past_date.strftime("%H:%M"),
            elapsed.seconds / 3600)
    if elapsed.seconds / 120:
        return "%s (%d minutes ago)" % (past_date.strftime("%H:%M"),
            elapsed.seconds / 60)
    if elapsed.seconds != 1:
        return "%d seconds ago" % elapsed.seconds
    return "1 second ago"


#
# Pull some methods out to here, need to think of a more desc. name
#
class BRMixin(object):

    @classmethod
    def clean_dict(self, dirty_dict):
        clean = {}
        valid_attributes = self.sqlmeta.columns.keys()
        for attr, value in dirty_dict.iteritems():
            if attr in valid_attributes:
                if isinstance(value, basestring):
                    value = value.strip()
                if attr == "myspace" and value:
                    value = value.split("/")[-1]
                clean[attr] = value
        return clean

    @classmethod
    def byNameI(self, name):
        try:
            name_col = self.q.name
        except AttributeError:
            name_col = self.q.user_name
        name = name.lower().strip()
        results = self.select(func.LOWER(name_col) == name)
        if results.count():
            return results[0]
        raise SQLObjectNotFound

    @classmethod
    def clone(cls, old, new):
        """Copy all links from one obj to another.

        new must already exist, and can have attrs/relations already.
        """
        if old == new:
            raise Exception
        # handle relatedjoins
        for join in [j for j in cls.sqlmeta.joins if isinstance(j, SORelatedJoin)]:
            add_func_name = "add" + join.addRemoveName
            addfunc = getattr(new, add_func_name)
            for item in getattr(old, join.joinMethodName):
                if item not in getattr(new, join.joinMethodName):
                    addfunc(item)
        # handle multiplejoins
        # we don't. broken for classes with MultipleJoins (another FK depends on)
        #for join in [j for j in cls.sqlmeta.joins if isinstance(j, SOMultipleJoin)]:
        #    q = "UPDATE %s SET %s = %s WHERE %s=%d" % \
        #        (join.otherClass.sqlmeta.table, join.joinColumn, self.id)
        #        self._connection.query(q)

        for field in old.sqlmeta.columns.keys():
            # only set if not set already
            if not getattr(new, field, None) and getattr(old, field, None):
                value = getattr(old, field)
                setattr(new, field, value)

    @classmethod
    def merge(cls, old, new):
        """Move relations from a duplicate entry to the real one, and
        remove the duplicate.
        """
        cls.clone(old, new)
        old.destroySelf()

#
# Classes inheriting from this will have changes stored in the UpdateLog table
#
class Journalled(SQLObject):
    created = DateTimeCol(default=datetime.now)
    approved = DateTimeCol(default=None)
    last_updated = DateTimeCol(default=datetime.now)

    def _get_fupdated(self):
        return fancy_date(self.last_updated)

    def _get_fcreated(self):
        return fancy_date(self.created)

def update_listener(instance, kwargs):
    skip_attrs = ('last_updated', 'approved', 'sims_updated', 'recordings_updated')
    # don't log changes until approved
    if not instance.approved:
        return
    for name, value in kwargs.items():
        old_value = getattr(instance, name, None)
        if old_value != value and name not in skip_attrs:
            try:
                current_user = identity.current.user.id
            except:
                current_user = None
            u = UpdateLog(
                changed_by=current_user,
                table_name=instance.sqlmeta.table,
                table_id=instance.id,
                attrib_name=name,
                attrib_old_value=old_value,
                attrib_new_value=value
                )
            kwargs['last_updated'] = datetime.now()

listen(update_listener, Journalled, RowUpdateSignal)

#
# Keep track of all edits to Journalled objects, so in case of vandalism,
# the changes can be reverted.
#
class UpdateLog(SQLObject):
    created = DateTimeCol(default=datetime.now)
    changed_by = IntCol()
    table_name = UnicodeCol(length=12)
    table_id = IntCol()
    attrib_name = UnicodeCol(length=20)
    attrib_old_value = UnicodeCol()
    attrib_new_value = UnicodeCol()

    def _get_attrib_old_value(self):
        return pickle.loads(str(self._SO_get_attrib_old_value()))
    
    def _set_attrib_old_value(self, value):
        self._SO_set_attrib_old_value(pickle.dumps(value))

    def _get_attrib_new_value(self):
        return pickle.loads(str(self._SO_get_attrib_new_value()))
    
    def _set_attrib_new_value(self, value):
        self._SO_set_attrib_new_value(pickle.dumps(value))

#
# Where events happen.
#
class Venue(Journalled, BRMixin):
    name = UnicodeCol(alternateID=True, length=100)
    description = UnicodeCol(default=None)
    address = UnicodeCol(default=None)
    url = UnicodeCol(length=256, default=None)
    myspace = UnicodeCol(length=50, default=None)
    phone = UnicodeCol(length=32, default=None)
    zip_code = UnicodeCol(length=10, default=None)
    geocode_lat = DecimalCol(size=11, precision=8, default=None)
    geocode_lon = DecimalCol(size=11, precision=8, default=None)
    added_by = ForeignKey('UserAcct', cascade=False)
    users = SQLRelatedJoin('UserAcct')
    events = SQLMultipleJoin('Event')

    @classmethod
    def merge(cls, old, new):
        # super handles everything but multiplejoins
        for event in old.events:
            event.venue = new
        super(Venue, cls).merge(old, new)

    @classmethod
    def closest(cls, location, count=5, with_event=False):
        from operator import itemgetter
        import geo
        pdx_lat, pdx_lon = "45.511810", "-122.675680"
        try:
            # lat is +, lon is -, a bug if otherwise
            lat, lon = geo.get_geocode(location)
            if not geo.is_within_radius(pdx_lat, pdx_lon, 15, lat, lon):
                return list()
            dist = 0.2
            got_result = False
            while not got_result:
                hi_lat, lo_lat, hi_lon, lo_lon = \
                    geo.radius_to_ll_bounds(lat, lon, dist)
                venues = Venue.select(AND(Venue.q.geocode_lat >= lo_lat,
                    Venue.q.geocode_lat <= hi_lat, Venue.q.geocode_lon >= lo_lon,
                    Venue.q.geocode_lon <= hi_lon))
                venues = list(venues)
                if with_event:
                    venues = [v for v in venues if v.today_events.count()] 
                if len(venues) >= count:
                    got_result = True
                else:
                    dist *= 2
        except IOError:
            return list()

        # sort by distance
        lst = [(v, geo.distance(lat, lon, v.geocode_lat, v.geocode_lon)) for v in venues]
        lst.sort(key=itemgetter(1))
        return lst[:count]

    def _get_future_events(self):
        return self.events.filter(
            AND(Event.q.date >= date.today(), Event.q.approved != None))

    def _get_today_events(self):
        return self.events.filter(
            AND(Event.q.date == date.today(), Event.q.approved != None))

    def _get_past_events(self):
        return self.events.filter(
            AND(Event.q.date < date.today(), Event.q.approved != None))

    def destroy_if_unused(self):
        if self.events.count() or self.users.count():
            return
        self.destroySelf()

#
# Data on bands/artists
#
class Artist(Journalled, BRMixin):
    name = UnicodeCol(alternateID=True, length=100)
    description = UnicodeCol(default=None)
    url = UnicodeCol(length=256, default=None)
    myspace = UnicodeCol(length=50, default=None)
    added_by = ForeignKey('UserAcct', cascade=False)
    sims_updated = DateTimeCol(default=None)
    recordings_updated = DateTimeCol(default=None)
    is_dj = BoolCol(default=False)
    events = SQLRelatedJoin('Event')
    users = SQLRelatedJoin('UserAcct')
    recordings = SQLMultipleJoin("Recording", joinColumn="by__id")


    def split_artist(self):
        u = identity.current.user
        import importers
        i = importers.Importers()
        new = list(i.artists_clean([self.name]))
        if len(new) > 1:
            a0 = Artist.byNameI(new[0])
            try:
                a1 = Artist.byNameI(new[1])
            except SQLObjectNotFound:
                a1 = Artist(name=new[1], added_by=u)
            Artist.clone(self.id, a1.id)
            Artist.merge(self.id, a0.id)
            return {a0.id:a0.name,a1.id:a1.name}
        else:
            return {self.id:self.name}

    @classmethod
    def merge(cls, old, new):
        # super handles everything but multiplejoins
        for recording in old.recordings:
            recording.by = new
        super(Artist, cls).merge(old, new)

    @classmethod
    def megamerge(cls):
        artists = Artist.select()
        out = []
        for artist in artists:
            variations = list(cls.name_variations(artist.name))
            for variation in variations[1:]:
                results = Artist.select(func.LOWER(Artist.q.name) == variation)
                if results.count():
                    out.append((results[0].id, artist.id))
        result_str = ""
        for a_id, b_id in out:
            try:
                a = Artist.get(a_id)
                b = Artist.get(b_id)
                if a.events.count() >= b.events.count():
                    new = a
                    old = b
                else:
                    new = b
                    old = a
                result_str += "merging %s into %s\n" % (old.name, new.name)
                cls.merge(old, new)
            except SQLObjectNotFound:
                # one of them already zapped, continue
                pass
        print result_str

    @classmethod
    def name_variations(cls, name):
        name = name.lower().strip()

        def pres(name):
            pres = ("the ", "dj ")
            yield name
            for pre in pres:
                if name.startswith(pre):
                    yield name[len(pre):]
                else:
                    yield pre + name

        def posts(name):
            posts = (" trio", " quartet", " band", " septet", " combo",
                     " jam", " jazz jam", " show", " and band", " ensemble")
            yield name
            for post in posts:
                if name.endswith(post):
                    yield name[:-len(post)]
                else:
                    yield name + post

        def replaces(name):
            replaces = ((" & ", " and "), (" and ", " & "))
            yield name
            for a, b in replaces:
                if name.find(a) != -1:
                    yield name.replace(a, b)

        # return all combinations of posts, pres, and replaces
        for pre in pres(name):
            for post in posts(pre):
                for replace in replaces(post):
                    yield replace


    @classmethod
    def byNameI(cls, name):
        try:
            return super(Artist, cls).byNameI(name)
        except  SQLObjectNotFound:
            for name_var in cls.name_variations(name):
                results = Artist.select(func.LOWER(Artist.q.name) == name_var)
                if results.count():
                    return results[0]
            raise SQLObjectNotFound

    def _get_future_events(self):
        return self.events.filter(Event.q.date >= date.today())

    def _get_past_events(self):
        return self.events.filter(Event.q.date < date.today())

    def _get_similars(self):
        similar_ids = [s.similar_artist.id for s in SimilarArtist.selectBy(artist=self)]
        if not similar_ids:
            # return empty set, but we always have to return a SelectResults
            return Artist.selectBy(id=None)
        return Artist.select((IN(Artist.q.id, similar_ids)))

    def _set_similars(self, artists):
        new_artists = set(artists)
        old_artists = set(s.similar_artist for s in SimilarArtist.selectBy(artist=self))
        to_remove = old_artists.difference(new_artists)
        to_add = new_artists.difference(old_artists)
        for artist in to_remove:
            sim = SimilarArtist.selectBy(artist=self, similar_artist=artist)[0]
            sim.destroySelf()
        for artist in to_add:
            sim = SimilarArtist(artist=self, similar_artist=artist)

    def destroySelf(self):
        # remove links to other artists
        for sim in SimilarArtist.selectBy(artist=self):
            sim.destroySelf()
        # remove links FROM other artist
        for sim in SimilarArtist.selectBy(similar_artist=self):
            # re-gen sim-links during batch, since now we're short
            sim.artist.sims_updated = None
            sim.destroySelf()
        super(Artist, self).destroySelf()

    def destroy_if_unused(self):
        if self.events.count() or self.users.count():
            return
        self.destroySelf()

#
# Link an Artist to similar Artists (bit of a hack)
#
class SimilarArtist(SQLObject):
    artist = ForeignKey('Artist', cascade=False)
    similar_artist = ForeignKey('Artist', cascade=False)

class Recording(SQLObject):
    created = DateTimeCol(default=datetime.now)
    name = UnicodeCol(length=200)
    by = ForeignKey('Artist', cascade=False)
    source = ForeignKey('Source', cascade=False)
    url = UnicodeCol(length=256, default=None)
    img_url = UnicodeCol(length=256, default=None)

#
# The most important class
#
class Event(Journalled, BRMixin):
    name = UnicodeCol(length=400)
    description = UnicodeCol(default=None)
    time = UnicodeCol(length=40, default=None)
    date = DateCol()
    cost = UnicodeCol(length=120, default=None)
    ages = UnicodeCol(length=40, default=None)
    url = UnicodeCol(length=256, default=None)
    ticket_url = UnicodeCol(length=256, default=None)
    venue = ForeignKey('Venue', cascade=False)
    added_by = ForeignKey('UserAcct', cascade=False)
    artists = SQLRelatedJoin('Artist')
    sources = SQLRelatedJoin('Source')
    attendances = SQLMultipleJoin('Attendance')
    date_index = DatabaseIndex('date')

    @classmethod
    def merge(cls, old, new):
        # super merge can't do multiplejoins
        for attendance in old.attendances:
            attendance.event = new

        # even if set, conditionally override some fields
        if old.created < new.created:
            new.created = old.created
        if not "admin" in old.added_by.groups:
            new.added_by = old.added_by
        super(Event, cls).merge(old, new)

    def _get_attendees(self):
        user_ids = [att.user.id for att in self.attendances]
        if not user_ids:
            return []
        return UserAcct.select((IN(UserAcct.q.id, user_ids)))

    def _get_has_djs(self):
        for artist in self.artists:
            if artist.is_dj:
                return True
        return False

    def _get_fdate(self):
        thedate = date.today()
        note = ""
        if self.date == thedate:
            note = " (today)"
        if self.date == thedate + timedelta(1):
            note = " (tomorrow)"
        return self.date.strftime("%a %m/%d/%y") + note

#
# User:Event M:M, with some add'l fields
#
class Attendance(Journalled):
    event = ForeignKey('Event', cascade=False)
    user = ForeignKey('UserAcct', cascade=False)
    planning_to_go = BoolCol(default=False)
    attended = BoolCol(default=False)
    comment = UnicodeCol(default=None)

#
# A record of each nightly batch run
#
class BatchRecord(SQLObject):
    # when the batch thread starts and finishes
    started = DateTimeCol(default=datetime.now)
    finished = DateTimeCol(default=None)
    # the period of new data it is processing
    first_handled = DateTimeCol(default=None)
    last_handled = DateTimeCol(default=None)
    email_sent = IntCol(default=0)
    artist_pings = IntCol(default=0)
    venue_pings = IntCol(default=0)
    sims_updated = IntCol(default=0)
    recordings_updated = IntCol(default=0)
    geocodes_updated = IntCol(default=0)

#
# Comments on the site
#
class Comment(SQLObject):
    created = DateTimeCol(default=datetime.now)
    comment = UnicodeCol()
    comment_by = ForeignKey('UserAcct', default=None, cascade=False)
    handled = BoolCol(default=False)

#
# Sources we import from
#
class Source(SQLObject):
    name = UnicodeCol(alternateID=True, length=100)
    created = DateTimeCol(default=datetime.now)
    events = SQLRelatedJoin('Event')


class VisitIdentity(SQLObject):
    visit_key = StringCol(length=40, alternateID=True,
                          alternateMethodName="by_visit_key")
    user_id = IntCol()
    expiry = DateTimeCol(default=None)


class Group(SQLObject):

    # names like "Group" and "Order" are reserved words in SQL
    # so we set the name to something safe for SQL
    class sqlmeta:
        table="tg_group"
    
    group_name = UnicodeCol(length=16, alternateID=True,
                            alternateMethodName="by_group_name")
    display_name = UnicodeCol(length=255)
    created = DateTimeCol(default=datetime.now)

    # collection of all users belonging to this group
    users = SQLRelatedJoin("UserAcct")

    # collection of all permissions for this group
    permissions = SQLRelatedJoin("Permission")

    def __cmp__(self, other):
        if isinstance(other, basestring):
            try:
                other = Group.by_group_name(other)
            except SQLObjectNotFound:
                return 1
        return cmp(self.group_name, other.group_name)


class UserAcct(SQLObject, BRMixin):
    user_name = UnicodeCol(length=16, alternateID=True,
                           alternateMethodName="by_user_name")
    email_address = UnicodeCol(length=255, alternateID=True,
                               alternateMethodName="by_email_address")
    password = UnicodeCol(length=40)
    # site-specific fields
    created = DateTimeCol(default=datetime.now)
    description = UnicodeCol(default=None)
    zip_code = UnicodeCol(length=10, default=None)
    url = UnicodeCol(length=256, default=None)
    myspace = UnicodeCol(length=50, default=None)
    last_emailed = DateTimeCol(default=None)
    event_email = BoolCol(default=True)
    other_email = BoolCol(default=False)
    artists = SQLRelatedJoin('Artist')
    venues = SQLRelatedJoin('Venue')
    groups = SQLRelatedJoin("Group")
    artists_added = SQLMultipleJoin("Artist", joinColumn="added__by__id")
    events_added = SQLMultipleJoin("Event", joinColumn="added__by__id")
    venues_added = SQLMultipleJoin("Venue", joinColumn="added__by__id")
    comments = SQLMultipleJoin("Comment", joinColumn="comment__by__id")
    attendances = SQLMultipleJoin("Attendance", joinColumn="user__id")

    def _get_events(self):
        event_ids = [att.event.id for att in self.attendances]
        if not event_ids:
            return []
        return Event.select((IN(Event.q.id, event_ids)))

    def _get_fcreated(self):
        return fancy_date(self.created)

    def _get_permissions(self):
        perms = set()
        for g in self.groups:
            perms = perms | set(g.permissions)
        return perms
        
    def _set_password(self, cleartext_password):
        "Runs cleartext_password through the hash algorithm before saving."
        hash = identity.encrypt_password(cleartext_password)
        self._SO_set_password(hash)
        
    def set_password_raw(self, password):
        "Saves the password as-is to the database."
        self._SO_set_password(password)


class Permission(SQLObject):
    permission_name = UnicodeCol(length=16, alternateID=True,
                                 alternateMethodName="by_permission_name")
    description = UnicodeCol(length=255)
    
    groups = SQLRelatedJoin("Group")

class FixupTable(SQLObject):
    name = UnicodeCol(alternateID=True)
    value = UnicodeCol()

class ArtistNameFixup(FixupTable):
    pass

class VenueNameFixup(FixupTable):
    pass
