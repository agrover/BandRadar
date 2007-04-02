from datetime import datetime, date, timedelta

from sqlobject import *
from turbogears.database import PackageHub
from turbogears import identity

import pickle

hub = PackageHub("bandradar")
__connection__ = hub

soClasses = ('UserAcct', 'Group', 'Permission', 'Venue', 'Artist',
             'SimilarArtist', 'Event', 'BatchRecord', 'Attendance',
             'Comment', 'UpdateLog', 'Source')

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


#
# Classes inheriting from this will have changes stored in the UpdateLog table
#
class Journalled(SQLObject):
    created = DateTimeCol(default=datetime.now)
    approved = DateTimeCol(default=None)
    last_updated = DateTimeCol(default=datetime.now)

    def __setattr__(self, name, value):
        if name in self.sqlmeta.columns.keys():
            self._record_update({name:value})
            super(Journalled, self).__setattr__('last_updated', datetime.now())
        super(Journalled, self).__setattr__(name, value)

    def set(self, **kw):
        self._record_update(kw)
        kw['last_updated'] = datetime.now()
        super(Journalled, self).set(**kw)

    def _record_update(self, updates):
        # don't log changes until approved
        if not getattr(self, "approved", None):
            return
        # don't log last_updated
        updates.pop('last_updated', None)
        updates.pop('approved', None)
        updates.pop('sims_updated', None)
        for name, value in updates.iteritems():
            old_value = getattr(self, name, None)
            if old_value != value:
                try:
                    current_user = identity.current.user.id
                except:
                    current_user = None
                u = UpdateLog(
                    changed_by=current_user,
                    table_name=self.sqlmeta.table,
                    table_id=self.id,
                    attrib_name=name,
                    attrib_old_value=old_value,
                    attrib_new_value=value
                    )
            # this records all vals to UpdateLog
            # super.set() can call our setattr() (overridden to update last_updated)
            # if we don't update the value here to its new value,
            #   the second call to _record_update will insert a duplicate row.
            super(Journalled, self).__setattr__(name, value)

    def _get_fupdated(self):
        return fancy_date(self.last_updated)

    def _get_fcreated(self):
        return fancy_date(self.created)


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

    def _get_future_events(self):
        return self.events.filter(Event.q.date >= date.today())

    def _get_past_events(self):
        return self.events.filter(Event.q.date < date.today())

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
    is_dj = BoolCol(default=False)
    events = SQLRelatedJoin('Event')
    users = SQLRelatedJoin('UserAcct')

    @classmethod
    def clean(cls, bad_snippet, good_snippet=""):
        """
        Rename artists with accidental crap in their name.
        If there is already a clean version, copy over links and
        remove the bad one.
        """
        artists = Artist.select(Artist.q.name.startswith(bad_snippet))
        for bad_artist in artists:
            # is there another artist with the name? move links over
            good_name = bad_artist.name.replace(bad_snippet, good_snippet)
            try:
                good_artist = Artist.byNameI(good_name)
                this.move(cls, bad_artist.id, good_artist.id)
            except SQLObjectNotFound:
                bad_artist.name = good_name

    @classmethod
    def move(cls, old_id, new_id):
        """Move relations from a duplicate entry to the real one, and
        remove the duplicate.
        """
        old = cls.get(old_id)
        new = cls.get(new_id)
        for event in old.events:
            if event not in new.events:
                new.addEvent(event)
            old.removeEvent(event)
        for user in old.users:
            if user not in new.users:
                new.addUserAcct(user)
            old.removeUserAcct(user)
        old.destroySelf()

    @classmethod
    def byNameI(cls, name):
        try:
            return super(Artist, cls).byNameI(name)
        except  SQLObjectNotFound:

            def name_variations(name):
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
                    posts = (" trio", " quartet", " band", " septet")
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

            for name_var in name_variations(name):
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
        for artist in old.artists:
            if artist not in new.artists:
                new.addArtist(artist)
        for source in old.sources:
            new.addSource(source)
        for field in old.sqlmeta.columns.keys():
            # only set if not set already
            if not getattr(new, field, None) and getattr(old, field, None):
                value = getattr(old, field)
                setattr(new, field, value)
        # even if set, conditionally override some fields
        if old.created < new.created:
            new.created = old.created
        if not "admin" in old.added_by.groups:
            new.added_by = old.added_by
        old.destroySelf()

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
    event_pings = IntCol(default=0)
    venue_pings = IntCol(default=0)

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
