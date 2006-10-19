import cherrypy
import turbogears
from turbogears import visit
from turbogears import identity
from sqlobject import SQLObjectNotFound
from model import UserAcct, VisitIdentity, hub
from datetime import datetime, timedelta
import time
import util

import logging
log = logging.getLogger("bandradar.saved_visit")

cookie_name = "saved_visit"


def saved_visit_is_on():
    "Returns True if config is properly enabled, False otherwise."
    return turbogears.config.get("visit.on", False) and \
        turbogears.config.get( "identity.on", False ) and \
        turbogears.config.get("saved_visit.on", False)

#Interface for the TurboGears extension
def start_extension():
    if not saved_visit_is_on():
        return
    log.debug("Saved Visit plugin starting")

    #Register the plugin for the Visit Tracking framework
    visit.enable_visit_plugin(SavedVisitPlugin())

def shutdown_extension():
    if not saved_visit_is_on():
        return
    
def remember(visit):
    months = 6
    future_time = datetime.utcnow() + timedelta(months*30)
    cherrypy.response.simple_cookie[cookie_name] = visit.key
    cherrypy.response.simple_cookie[cookie_name]['path'] = "/"
    # use official Netscape cookie time format, bleh
    cherrypy.response.simple_cookie[cookie_name]['expires'] = \
        future_time.strftime("%a, %d-%b-%Y %X GMT")
    return future_time

def forget():
    cherrypy.response.simple_cookie[cookie_name] = "_"
    cherrypy.response.simple_cookie[cookie_name]['path'] = "/"
    cherrypy.response.simple_cookie[cookie_name]['expires'] = 0    

class SavedVisitPlugin(object):
    
    def __init__(self):
        #log.debug("SavedVisitPlugin extension starting")
        pass

    def record_request(self, visit):
        if identity.current.user:
            # if we are logged in, watch for the "remember" param, and set the
            # cookie if so.
            if cherrypy.request.params.pop("remember", None):
                vi = VisitIdentity.by_visit_key(visit.key)
                vi.expiry = remember(visit)
        else:
            # if we're not logged in, see if the cookie is there, and log in
            try:
                saved_key = cherrypy.request.simple_cookie[cookie_name].value
                vi = VisitIdentity.by_visit_key(saved_key)
                u = UserAcct.get(vi.user_id)
                identity.current_provider.validate_identity(u.user_name,
                    u.password, visit.key)
                # must commit or db will forget we logged in, when we 
                # redirect (rollback) below
                hub.commit()
                # reload, since now we're logged in
                turbogears.redirect(cherrypy.request.path)
            except (KeyError, SQLObjectNotFound):
                pass
