import cherrypy
import turbogears
from turbogears import visit
from turbogears import identity
from sqlobject import SQLObjectNotFound
from model import UserAcct, hub
from datetime import datetime, timedelta
import time
import util

import logging
log = logging.getLogger("bandradar.saved_visit")


def saved_visit_is_on():
    "Returns True if ip tracking is properly enabled, False otherwise."
    return cherrypy.config.get('visit.on', False)# and cherrypy.config.get('visit.saved_visit.on', False)

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
    
def remember(user):
    months = 6
    future_time = datetime.utcnow() + timedelta(months*30)
    cherrypy.response.simple_cookie['userName'] = user.user_name
    cherrypy.response.simple_cookie['userName']['path'] = "/"
    # use official Netscape cookie time format, bleh
    cherrypy.response.simple_cookie['userName']['expires'] = \
        future_time.strftime("%a, %d-%b-%Y %X GMT")

def forget():
    cherrypy.response.simple_cookie['userName'] = "_"
    cherrypy.response.simple_cookie['userName']['path'] = "/"
    cherrypy.response.simple_cookie['userName']['expires'] = 0    

class SavedVisitPlugin(object):
    
    def __init__(self):
        #log.debug("SavedVisitPlugin extension starting")
        pass

    def record_request(self, visit):
        if not identity.current.anonymous:
            # if we are logged in, watch for the "remember" param, and set the
            # cookie if so.
            if cherrypy.request.params.pop("remember", None):
                remember(identity.current.user)
        else:
            # if we're not logged in, see if the cookie is there, and log in
            try:
                username = cherrypy.request.simple_cookie['userName'].value
                u = UserAcct.by_user_name(username)
                identity.current_provider.validate_identity(u.user_name,
                    u.password, visit.key)
                # must commit or db will forget we logged in, when we 
                # redirect (rollback) below
                hub.commit()
                # reload, since now we're logged in
                turbogears.redirect(cherrypy.request.path)
            except (KeyError, SQLObjectNotFound):
                pass
