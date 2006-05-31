import cherrypy
from turbogears import visit
from model import VisitIP

def saved_visit_is_on():
    "Returns True if ip tracking is properly enabled, False otherwise."
    return cherrypy.config.get('visit.on', False) and cherrypy.config.get('visit.saved_visit.on', False)

#Interface for the TurboGears extension
def start_extension():
    if not saved_visit_is_on():
        return
    cherrypy.log( "Visit ip tracker starting" )

    #Register the plugin for the Visit Tracking framework
    visit.enable_visit_plugin( IPVisitPlugin() )
    
def shutdown_extension():
    if not saved_visit_is_on():
        return
    cherrypy.log( "Saved Visit pluginshutting down" )
    
class SavedVisitPlugin(object):
    
    def __init__(self):
        cherrypy.log("SavedVisitPlugin extension starting")
    
    def record_request(self, visit_id):
        # This method gets called on every single visit, so if you 
        # want to record something every time they make a request, this
        # is the place to do it.
        pass
        
    def new_visit(self, visit_id):
        # This method gets called the first time the visit is started.
        # I think IP tracking makes sense in here.
        v = visit.TG_Visit.get(visit_id)
        
        # add a new visit ip object to the database
        VisitIP(visit=v, ip_address=cherrypy.request.remoteAddr)
        
