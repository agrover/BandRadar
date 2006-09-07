from datetime import datetime

from sqlobject import *
from turbogears.database import PackageHub
from turbogears import identity

hub = PackageHub("bandradar")
__connection__ = hub

soClasses = ('UserAcct', 'Group', 'Permission', 'Venue', 'Artist', 'Event',
             'BatchRecord', 'Attendance')


class Venue(SQLObject):
    name = UnicodeCol(alternateID=True, length=100)
    address = UnicodeCol(default=None)
    url = UnicodeCol(length=256, default=None)
    phone = UnicodeCol(length=12, default=None)
    created = DateTimeCol(default=datetime.now())
    added_by = ForeignKey('UserAcct', default=None)
    last_updated = DateTimeCol(default=datetime.now())
    verified = BoolCol(default=False)
    active = BoolCol(default=True)


class Artist(SQLObject):
    name = UnicodeCol(alternateID=True, length=100)
    description = UnicodeCol(default=None)
    url = UnicodeCol(length=256, default=None)
    events = RelatedJoin('Event')
    users = RelatedJoin('UserAcct')
    created = DateTimeCol(default=datetime.now())
    added_by = ForeignKey('UserAcct', default=None)
    last_updated = DateTimeCol(default=datetime.now())
    verified = BoolCol(default=False)
    active = BoolCol(default=True)


class Event(SQLObject):
    name = UnicodeCol(length=200)
    description = UnicodeCol(default=None)
    time = UnicodeCol(length=20, default=None)
    date = DateCol()
    cost = UnicodeCol(length=60, default=None)
    ages = UnicodeCol(length=20, default=None)
    url = UnicodeCol(length=256, default=None)
    venue = ForeignKey('Venue')
    added_by = ForeignKey('UserAcct', default=None)
    artists = RelatedJoin('Artist')
    created = DateTimeCol(default=datetime.now())
    added_by = ForeignKey('UserAcct', default=None)
    last_updated = DateTimeCol(default=datetime.now())
    verified = BoolCol(default=False)
    active = BoolCol(default=True)
    event_index = DatabaseIndex('date', 'time', 'venue', unique=True)


class Attendance(SQLObject):
    event = ForeignKey('Event')
    user = ForeignKey('UserAcct')
    comment = UnicodeCol(default=None)
    planning_to_go = BoolCol(default=False)
    attended = BoolCol(default=False)
    created = DateTimeCol(default=datetime.now())
    last_updated = DateTimeCol(default=datetime.now())


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
    """
    An ultra-simple group definition.
    """
    
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


class UserAcct(SQLObject):
    """
    Reasonably basic User definition. Probably would want additional attributes.
    """
    user_name = UnicodeCol( length=16, alternateID=True,
                           alternateMethodName="by_user_name" )
    email_address = UnicodeCol( length=255, alternateID=True,
                               alternateMethodName="by_email_address" )
    display_name = UnicodeCol( length=255 )
    password = UnicodeCol( length=40 )
    created = DateTimeCol( default=datetime.now )
    # site-specific fields
    zip_code = UnicodeCol(length=10, default=None)
    url = UnicodeCol(length=256, default=None)
    artists = RelatedJoin('Artist')
    events = RelatedJoin('Event')
    last_updated = DateTimeCol(default=datetime.now())
    last_emailed = DateTimeCol(default=None)
    event_email = BoolCol(default=True)
    other_email = BoolCol(default=False)

    # groups this user belongs to
    groups = RelatedJoin( "Group")

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
