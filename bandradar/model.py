from datetime import datetime, date, timedelta

from sqlobject import *
from turbogears.database import PackageHub
from turbogears import identity

hub = PackageHub("bandradar")
__connection__ = hub

soClasses = ('UserAcct', 'Group', 'Permission', 'Venue', 'Artist', 'Event',
             'BatchRecord', 'Attendance', 'Comment', 'UpdateLog')

def artist_clean(bad_snippet, good_snippet=""):
    """
    Rename artists with accidental crap in their name.
    If there is already a clean version, copy over links and remove the bad one.
    """
    artists = Artist.select(Artist.q.name.startswith(bad_snippet))
    for bad_artist in artists:
        # is there another artist with the name? move links over
        good_name = bad_artist.name.replace(bad_snippet, "")
        try:
            good_artist = Artist.byNameI(good_name)
            for event in bad_artist.events:
                good_artist.addEvent(event)
                bad_artist.removeEvent(event)
            for user in bad_artist.users:
                good_artist.addUser(user)
                bad_artist.removeUser(user)
            bad_artist.destroySelf()
        except SQLObjectNotFound:
            bad_artist.name = good_name

def artist_move(old_id, new_id):
    old = Artist.get(old_id)
    new = Artist.get(new_id)
    for event in old.events:
        new.addEvent(event)
        old.removeEvent(event)
    for user in old.users:
        new.addUser(user)
        old.removeUser(user)
    old.destroySelf()

class BRSQLObject(SQLObject):
    created = DateTimeCol(default=datetime.now())
    approved = DateTimeCol(default=None)
    last_updated = DateTimeCol(default=datetime.now())
    description = UnicodeCol(default=None)

    def __setattr__(self, name, value):
        """When an attribute changes, update last_updated, and if the change is to
        an approved object, log it.
        """
        if name in self.sqlmeta.columns.keys():
            old_value = str(getattr(self, name, None))
            new_value = str(value)
            if old_value != new_value:
                super(BRSQLObject, self).__setattr__('last_updated', datetime.now())
                if self.approved:
                    try:
                        current_user = identity.current.user
                    except:
                        current_user = None
                    u = UpdateLog(
                        changed_by=current_user,
                        table_name=self.__class__.__name__,
                        table_id=self.id,
                        attrib_name=name,
                        attrib_old_value=old_value,
                        attrib_new_value=new_value
                        )
        super(BRSQLObject, self).__setattr__(name, value)

    @classmethod
    def byNameI(self, name):
        results = self.select(func.LOWER(self.q.name) == name.lower())
        if results.count() == 0:
            raise SQLObjectNotFound
        else:
            return results[0]

    def _fdate(self, past_date):
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
        return "%d seconds ago" % elapsed.seconds

    def get_fupdated(self):
        return self._fdate(self.last_updated)

    def get_fcreated(self):
        return self._fdate(self.created)

    @classmethod
    def clean_dict(self, dirty_dict):
        clean = {}
        valid_attributes = self.sqlmeta.columns.keys()
        for attr, value in dirty_dict.iteritems():
            if attr in valid_attributes:
                if isinstance(value, basestring):
                    value = value.strip()
                clean[attr] = value
        return clean

class UpdateLog(SQLObject):
    created = DateTimeCol(default=datetime.now())
    changed_by = IntCol()
    table_name = UnicodeCol(length=12)
    table_id = IntCol()
    attrib_name = UnicodeCol(length=20)
    attrib_old_value = UnicodeCol()
    attrib_new_value = UnicodeCol()

class Venue(BRSQLObject):
    name = UnicodeCol(alternateID=True, length=100)
    address = UnicodeCol(default=None)
    url = UnicodeCol(length=256, default=None)
    phone = UnicodeCol(length=32, default=None)
    added_by = ForeignKey('UserAcct')


class Artist(BRSQLObject):
    name = UnicodeCol(alternateID=True, length=100)
    url = UnicodeCol(length=256, default=None)
    events = SQLRelatedJoin('Event')
    users = SQLRelatedJoin('UserAcct')
    added_by = ForeignKey('UserAcct')

    def destroySelf(self):
        for e in self.events:
            self.removeEvent(e)
        for u in self.users:
            self.removeUserAcct(u)        
        super(Artist, self).destroySelf()

    def destroy_if_unused(self):
        if self.events.count() or self.users.count():
            return
        self.destroySelf()


class Event(BRSQLObject):
    name = UnicodeCol(length=400)
    time = UnicodeCol(length=40, default=None)
    date = DateCol()
    cost = UnicodeCol(length=120, default=None)
    ages = UnicodeCol(length=40, default=None)
    url = UnicodeCol(length=256, default=None)
    venue = ForeignKey('Venue')
    artists = SQLRelatedJoin('Artist')
    added_by = ForeignKey('UserAcct')
    event_index = DatabaseIndex('date', 'time', 'venue', unique=True)
    date_index = DatabaseIndex('date')

    def destroySelf(self):
        for a in self.artists:
            self.removeArtist(a)
        super(Event, self).destroySelf()

    def get_fdate(self):
        thedate = date.today()
        note = ""
        if self.date == thedate:
            note = " (today)"
        if self.date == thedate + timedelta(1):
            note = " (tomorrow)"
        return self.date.strftime("%a %m/%d") + note


class Attendance(BRSQLObject):
    event = ForeignKey('Event')
    user = ForeignKey('UserAcct')
    planning_to_go = BoolCol(default=False)
    attended = BoolCol(default=False)


class BatchRecord(SQLObject):
    # when the batch thread starts and finishes
    started = DateTimeCol(default=datetime.now)
    finished = DateTimeCol(default=None)
    # the period of new data it is processing
    first_handled = DateTimeCol(default=None)
    last_handled = DateTimeCol(default=None)
    email_sent = IntCol(default=0)

class Comment(SQLObject):
    created = DateTimeCol(default=datetime.now)
    comment = UnicodeCol()
    comment_by = IntCol(default=None)

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
    
    group_name = UnicodeCol( length=16, alternateID=True,
                            alternateMethodName="by_group_name" )
    display_name = UnicodeCol( length=255 )
    created = DateTimeCol( default=datetime.now )

    # collection of all users belonging to this group
    users = SQLRelatedJoin( "UserAcct")

    # collection of all permissions for this group
    permissions = SQLRelatedJoin( "Permission")

    def __cmp__(self, other):
        if isinstance(other, basestring):
            other = Group.by_group_name(other)
        return cmp(self.group_name, other.group_name)


class UserAcct(BRSQLObject):
    user_name = UnicodeCol(length=16, alternateID=True,
                           alternateMethodName="by_user_name")
    email_address = UnicodeCol(length=255, alternateID=True,
                               alternateMethodName="by_email_address")
    password = UnicodeCol(length=40)
    # site-specific fields
    zip_code = UnicodeCol(length=10, default=None)
    url = UnicodeCol(length=256, default=None)
    artists = SQLRelatedJoin('Artist')
    last_emailed = DateTimeCol(default=None)
    event_email = BoolCol(default=True)
    other_email = BoolCol(default=False)
    # groups this user belongs to
    groups = SQLRelatedJoin( "Group")

    def destroySelf(self):
        for a in self.artists:
            self.removeEvent(a)
        for g in self.groups:
            self.removeGroup(g)        
        super(UserAcct, self).destroySelf()

    def _get_permissions( self ):
        perms = set()
        for g in self.groups:
            perms = perms | set(g.permissions)
        return perms
        
    def _set_password( self, cleartext_password ):
        "Runs cleartext_password through the hash algorithm before saving."
        hash = identity.encrypt_password(cleartext_password)
        self._SO_set_password(hash)
        
    def set_password_raw( self, password ):
        "Saves the password as-is to the database."
        self._SO_set_password(password)


class Permission(SQLObject):
    permission_name = UnicodeCol(length=16, alternateID=True,
                                 alternateMethodName="by_permission_name")
    description = UnicodeCol(length=255)
    
    groups = SQLRelatedJoin("Group")
