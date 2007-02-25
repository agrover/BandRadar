## Start by getting an xml parser in here. We can work with mini
try:
    from xml.dom.ext.reader import Sax2
    parse_xml = Sax2.FromXml
    __xml = "pyxml"
except ImportError:
    from xml.dom.minidom import parseString as parse_xml 
    __xml = "standard"

import urllib
from ConfigParser import SafeConfigParser
import os.path


## Constants and Configuration Stuff

configDefaults = {"password":"",
                  "username":"",
                  "api_key":""}
                  
config = SafeConfigParser(configDefaults)

config.read(['upcoming.conf',
            'bandradar/config/upcoming.conf',
            os.path.expanduser('~/.upcoming/upcoming.conf')])

__password = config.get("general", "password")
__username = config.get("general", "username")
__api_key = config.get("general", "api_key")

_always_auth = config.getboolean("general", "always_auth")
__quick_api = config.getboolean("general", "quick_api")


REST_URL = config.get("general", "rest_url")

O = 0
R = 1

ELEMENT_NODE = 1
ATTRIBUTE_NODE = 2
TEXT_NODE = 3

## API definition / object
#   It may be neat to, in the future, yank this API def out of the code
#   and put it somewhere else so that it can be updated more easily

class api:
    __sub = {}
    __sub['event'] = \
        {"calls":
            {"add":{"auth_required":1,
                    "request_type":"POST",
                    "args":{
                        "name":R,
                        "metro_id":R,
                        "venue_id":R,
                        "category_id":R,
                        "start_date":R,
                        "end_date":O,
                        "start_time":O,
                        "end_time":O,
                        "description":O,
                        "personal":O,
                        "selfpromotion":O}},
             "getInfo":{"args":{
                            "event_id":R,
                            "username":O,
                            "password":O}},
             "search":{"args":{
                            "search_text":O,
                            "country_id":O,
                            "state_id":O,
                            "metro_id":O,
                            "category_id":O,
                            "venue_id":O,
                            "min_date":O,
                            "max_date":O,
                            "tags":O,
                            "per_page":O,
                            "page":O,
                            "sort":O,
                            "username":O,
                            "password":O}},
             "getWatchlist":{"auth_required":1,
                             "args":{"event_id":R}}}}
    
    __sub['metro'] = \
        {"calls":
            {"getInfo":{"args":{"metro_id":R}},
             "getList":{"args":{"state_id":R}},
             "getStateList":{"args":{"country_id":R}},
             "getCountryList":{},
             "search":{"auth_required":1,
                       "args":{
                            "search_text":O,
                            "country_id":O,
                            "state_id":O}}}}
    
    __sub['venue'] = \
        {"calls":
            {"add":{"auth_required":1,
                    "request_type":"POST",
                    "args":{
                        "venuename":R,
                        "venueaddress":R,
                        "venuecity":R,
                        "metro_id":R,
                        "venuezip":O,
                        "venuephone":O,
                        "venueurl":O,
                        "venuedescription":O,
                        "private":O}},
             "getInfo":{"args":{
                            "venue_id":R,
                            "username":O,
                            "password":O}},
             "getList":{"args":{
                            "metro_id":R,
                            "username":O,
                            "password":O}},
             "search":{"args":{
                            "search_text":O,
                            "country_id":O,
                            "state_id":O,
                            "metro_id":O,
                            "username":O,
                            "password":O}}}}

    __sub['category'] = \
        {"calls":{"getList":{}}}
    
    __sub['watchlist'] = \
        {"calls":
            {"add":{"auth_required":1,
                    "request_type":"POST",
                    "args":{
                        "event_id":R,
                        "status":O}},
             "getList":{"auth_required":1,
                        "args":{
                            "min_date":O,
                            "max_date":O}},
             "remove":{"auth_required":1,
                       "request_type":"POST",
                       "args":{"watchlist_id":R}}}}
    
    __sub['user'] = \
        {"calls":
            {"getInfo":{"args":{
                            "user_id":R,
                            "username":O,
                            "password":O}},
             "getMetroList":{"auth_required":1},
             "getWatchlist":{"auth_required":1}}}
    
    __name = "upcoming"
    __call = {} 
    
    def __init__(self,name=None,subs=None,calls=None):
        if name is not None: self.__name = name
        if subs is not None: self.__sub = subs
        if calls is not None: self.__call = calls
        
    def __getattr__(self,name):
        if self.__call.has_key(name):
            self.__dict__[name] = \
                generateApiCall("%s.%s"%(self.__name,name),
                                self.__call[name])
            return self.__dict__[name]
        elif self.__sub.has_key(name):
            if not self.__sub[name].has_key("subs"): 
                self.__sub[name]['subs'] = {}
            self.__dict__[name] = api(name="%s.%s"%(self.__name,name),
                                      subs=self.__sub[name]['subs'],
                                      calls=self.__sub[name]['calls'])
            return self.__dict__[name]
        raise AttributeError, name

__api = api()
def get_api():
    return __api

## Base models
#   These may be a bit overkill, but they make working with everything
#   much nicer

class Base(object):
    def __init__(self,nodeName=None,**kwargs):
        for x,y in kwargs.iteritems():
            setattr(self,x,y)
        self.__children = []
            
    def __getattr__(self,name):
        if hasattr(self,'_get_%s'%(name)):
            self.__dict__[name] = getattr(self,'_get_%s'%(name))()
            return self.__dict__[name]
        raise AttributeError, name
    
    def __getitem__(self,key):
        return self.__children[key]

    def __setitem__(self,key,value):
        self.__children[key] = value
    
    def __delitem__(self,key):
        del self.__children[key]
        
    def __len__(self):
        return len(self.__children)    
    
    def append(self,value):
        self.__children.append(value)
    
    def items(self):
        return self.__children
    
    def _get_logger(self):
        pass
    
    def _get_api(self):
        return get_api()
    
    def _get_value(self):
        return self.id
    
    # yeah, these next two will cause errors if called. That's why they you
    # shouldn't call them ;)
    def log(self,level,msg):
        """If a logger isn't defined, set one up and then log the event"""
        return self.logger.log(level,msg)

    def error(self,msg):
        """We probably want to raise an exception, too, or whatever"""
        return self.log("error",msg)

    
    def fromElement(self,element):
        if element.attributes:
            for i in range(element.attributes.length):
                x = element.attributes.item(i)
                setattr(self,x.name,x.value)
        self.nodeName = element.nodeName
        if element.childNodes.length == 1 and \
           element.childNodes[0].nodeType == TEXT_NODE:
            self.value = element.childNodes[0].nodeValue
        elif element.childNodes and self.__class__ == Base:
            self.fromElementChildrenToList(element)
            self.fromElementChildrenToAttributes(element)
        return self
    
    def fromElementChildrenToList(self,element):
        for x in element.childNodes:
            if x.nodeType == ELEMENT_NODE:
                self.append(fromElement(x))
        return self
    
    def fromElementChildrenToAttributes(self,element):
        for x in element.childNodes:
            if x.nodeType == ELEMENT_NODE:
                a = fromElement(x)
                if len(x.childNodes) > 1 or len(x.attributes):
                    setattr(self,a.nodeName,a)
                else:
                    setattr(self,a.nodeName,a.value)
        return self
    
    def fromElementChildrenToDict(self,element):
        for x in element.childNodes:
            if x.nodeType == ELEMENT_NODE:
                a = fromElement(x)
                self[a.value] = a
        return self

class BaseList(Base):
    def fromElement(self,element):
        Base.fromElement(self,element)
        self.fromElementChildrenToList(element)
        return self

    def _get_value(self):       
        value = {}
        for x in self.items():
            value[x.value] = x
        return value

class BaseDict(Base):
    def __init__(self,nodeName=None,**kwargs):
        for x,y in kwargs.iteritems():
            setattr(self,x,y)
        self.__children = {}
    
    def fromElement(self,element):
        Base.fromElement(self,element)
        self.fromElementChildrenToDict(element)
        return self
    
    def __getitem__(self,key):
        return self.__children[key]

    def __setitem__(self,key,value):
        self.__children[key] = value
    
    def __delitem__(self,key):
        del self.__children[key]
        
    def __len__(self):
        return len(self.__children)    
    
    def keys(self):
        return self.__children.keys()

    def values(self):
        return self.__children.values()

    def items(self):
        return self.__children.items()

## --MODELS--

#   I realize these all use the same base class, but ya know... if upcoming
#   decided to do something crazy... I'D BE READY FOR THEM.

class Event(Base):
    def _get_venue(self):
        try:
            venue = self.api.venue.getInfo(venue_id=self.venue_id)[0]
        except IndexError:
            venue = Venue(id=self.venue_id)
        return venue
    
    def _get_user(self):
        try:
            user = self.api.user.getInfo(user_id=self.user_id)[0]
        except IndexError:
            user = User(id=self.user_id)
        return user
    
    def _get_category(self):
        try:
            category = self.api.category.getInfo(category_id=self.category_id)[0]
        except IndexError:
            category = Category(id=self.category_id)
        return category

class Venue(Base):
    def events(self):
        return self.api.event.search(venue_id=self.id)
    
    def _get_user(self):
        try:
            user = self.api.user.getInfo(user_id=self.user_id)[0]
        except IndexError:
            user = User(id=self.user_id)
        return user

class Metro(Base):
    def events(self,**kwargs):
        return self.api.event.search(metro_id=self.id,**kwargs)

    def venues(self,**kwargs):
        return  self.api.venue.getList(metro_id=self.id,**kwargs)


class State(Base):
    def metros(self,**kwargs):
        return self.api.metro.getList(state_id=self.id,**kwargs)
    
class Country(Base):
    def states(self,**kwargs):
        return self.api.metra.getStateList(country_id=self.id,**kwargs)

class User(Base):
    def events(self,**kwargs):
        return self.api.user.getWatchlist(user_id=self.id,**kwargs)

class Category(Base):
    pass

class Watchlist(Base):
    def _get_event(self):
        try:
            event = self.api.event.getInfo(event_id=self.event_id)[0]
        except IndexError:
            event = Event(id=self.event_id)
        return event

    def remove(self,**kwargs):
        return self.api.watchlist.remove(watchlist_id=self.id,**kwargs)


## Models - Errors

class Error(Base):
    def fromElement(self,element):
        raise Exception("%s"%(element.attributes.getNamedItem("msg").value))

## Helper Functions

def fromElement(element):
    try:
        objList = globals()
        ind = {}
        for x in objList.keys():
            if type(objList[x]) is type(Base) and issubclass(objList[x],Base):
                ind[x.lower()] = objList[x]
        obj = ind[element.nodeName]()
        
    except Exception, err:
        print err
        obj = Base()
    return obj.fromElement(element)

def parseResponse(xml):
    doc = parse_xml(xml)
    #doc = Sax2.FromXml(xml)
    rspChildren = doc.getElementsByTagName("rsp")
    if len(rspChildren):
        rsp = rspChildren[0]
        if rsp.attributes.getNamedItem("stat").value == "fail":
            return Error().fromElement(rsp.getElementsByTagName("error")[0])
        out_list = []
        for x in rsp.childNodes:
            if x.nodeType == ELEMENT_NODE: 
                out_list.append(fromElement(x))
        return out_list
    raise Exception("Nothing found?")
    
def generateApiCall(name,skel):
    args = skel.get("args",{})
    args['api_key'] = R
    auth_required = skel.get("auth_required",0)
    if _always_auth == "1":
        auth_required = 1
        
    # upcoming.org doesn't use a base namespace, strip it
    if name[:9] == "upcoming.":
        name = name[9:]
    request_type = skel.get("request_type","GET")
    
    def methodWrapper(method=name,request_type=request_type,**kwargs):
        kwargs['api_key'] = __api_key
        for arg, options in args.iteritems():
            if options == R:
                if not kwargs.has_key(arg) or kwargs[arg] is None:
                    raise AssertionError("%s must be set"%(arg))
        if auth_required:
            kwargs['username'] = __username
            kwargs['password'] = __password
            assert kwargs.has_key("username") and \
                    kwargs["username"] is not None
            assert kwargs.has_key("password") and \
                    kwargs["password"] is not None
        kwargs['api_url'] = skel.get('api_url',REST_URL)
        return apiCall(method=name,request_type=request_type,**kwargs)
    
    methodWrapper.name = name
    methodWrapper.args = args
    methodWrapper.auth_required = auth_required
    methodWrapper.request_type = request_type
    return methodWrapper
    
def apiHelp(call):
    argList = []
    if call.auth_required:
        argList.append("username")
        argList.append("password")
    for arg,options in call.args.iteritems():
        if options == R:
            argList.append("%s"%(arg))
        elif options == O:
            argList.append("[%s]"%(arg))
    print "%s(%s)"%(call.name,", ".join(argList))

def apiCall(test=False,api_url=None,request_type=None,**kwargs):
    if request_type == 'GET':
        r = urllib.urlopen("%s?%s"%(api_url,urllib.urlencode(kwargs))).read()
    elif request_type == 'POST':
        r = urllib.urlopen(api_url,urllib.urlencode(kwargs)).read()
    return parseResponse(r)

## More crazy interfaces
#   See documentation for the "quick api" in the README
if __quick_api:
    event = __api.event
    metro = __api.metro
    venue = __api.venue
    category = __api.category
    watchlist = __api.watchlist
    user = __api.user
