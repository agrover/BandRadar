from datetime import datetime, date, timedelta

from sqlobject import *
from turbogears.database import PackageHub
from turbogears import identity

hub = PackageHub("bandradar")
__connection__ = hub

soClasses = ('UserAcct', 'Group', 'Permission', 'Venue', 'Artist', 'Event',
             'BatchRecord', 'Attendance')

class BRSQLObject(SQLObject):

    created = DateTimeCol(default=datetime.now())
    last_updated = DateTimeCol(default=datetime.now())
    description = UnicodeCol(default=None)

    def __setattr__(self, name, value):
        super(BRSQLObject, self).__setattr__(name, value)
        if name in self.sqlmeta.columns.keys():
            super(BRSQLObject, self).__setattr__('last_updated', datetime.now())

    def _fdate(self, past_date):
        elapsed = datetime.now() - past_date
        if elapsed.days:
            return "%s (%d days ago)" % (past_date.strftime("%x"), elapsed.days)
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

class Venue(BRSQLObject):
    name = UnicodeCol(alternateID=True, length=100)
    address = UnicodeCol(default=None)
    url = UnicodeCol(length=256, default=None)
    phone = UnicodeCol(length=32, default=None)
    added_by = ForeignKey('UserAcct')
    verified = BoolCol(default=False)
    active = BoolCol(default=True)


class Artist(BRSQLObject):
    name = UnicodeCol(alternateID=True, length=100)
    url = UnicodeCol(length=256, default=None)
    events = RelatedJoin('Event')
    users = RelatedJoin('UserAcct')
    added_by = ForeignKey('UserAcct')
    verified = BoolCol(default=False)
    active = BoolCol(default=True)

    def destroySelf(self):
        for e in self.events:
            self.removeEvent(e)
        for u in self.users:
            self.removeUserAcct(u)        
        super(Artist, self).destroySelf()

    def destroy_if_unused(self):
        if self.events or self.users:
            return
        self.destroySelf()


class Event(BRSQLObject):
    name = UnicodeCol(length=200)
    time = UnicodeCol(length=20, default=None)
    date = DateCol()
    cost = UnicodeCol(length=60, default=None)
    ages = UnicodeCol(length=20, default=None)
    url = UnicodeCol(length=256, default=None)
    venue = ForeignKey('Venue')
    artists = RelatedJoin('Artist')
    added_by = ForeignKey('UserAcct')
    verified = BoolCol(default=False)
    active = BoolCol(default=True)
    event_index = DatabaseIndex('date', 'time', 'venue', unique=True)
    date_index = DatabaseIndex('date')

    def destroySelf(self):
        for a in self.artists:
            self.removeArtist(a)
        super(Event, self).destroySelf()

    def get_fdate(self):
        thedate = date.today()
        if self.date == thedate:
            return "today"
        if self.date == thedate + timedelta(1):
            return "tomorrow"
        return self.date.strftime("%a %m/%d")


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


class VisitIdentity(SQLObject):
    visit_key = StringCol( length=40, alternateID=True,
                          alternateMethodName="by_visit_key" )
    user_id = IntCol()


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
    users = RelatedJoin( "UserAcct")

    # collection of all permissions for this group
    permissions = RelatedJoin( "Permission")

    def __cmp__(self, other):
        if isinstance(other, basestring):
            other = Group.by_group_name(other)
        return cmp(self.group_name, other.group_name)

class UserAcct(BRSQLObject):
    user_name = UnicodeCol( length=16, alternateID=True,
                           alternateMethodName="by_user_name" )
    email_address = UnicodeCol( length=255, alternateID=True,
                               alternateMethodName="by_email_address" )
    password = UnicodeCol( length=40 )
    # site-specific fields
    zip_code = UnicodeCol(length=10, default=None)
    url = UnicodeCol(length=256, default=None)
    artists = RelatedJoin('Artist')
    last_emailed = DateTimeCol(default=None)
    event_email = BoolCol(default=True)
    other_email = BoolCol(default=False)
    # groups this user belongs to
    groups = RelatedJoin( "Group")

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
    permission_name = UnicodeCol( length=16, alternateID=True,
                                 alternateMethodName="by_permission_name" )
    description = UnicodeCol( length=255 )
    
    groups = RelatedJoin( "Group")
