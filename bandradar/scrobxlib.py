"""
audioscrobbler REST API XML processing library

This libarary implements an python programming interface to the
REST (Representational State Transfer) web services interface
provideded by Last.fm/Audioscrobbler.

If you don't already know, last.fm is a site built around a
community of users who share Music metadata. It tracks how
often songs are played, etc. by using plugins/media players
that update the site as you listen to music.

This module currently implements are large chunk of the possible
xml feeds that audioscrobbler generates. The easyest way to use
this module is to use the fetch-functions. These are named like:
    topArtists
    topTracks
    topAlbums
    etc...


This module can also be extended by implementing subclasses of
the ScrobHandler class. The library uses the SAX xml parser to
do the heavy lifting. Please examine the python docstrings/code
to see how to do that.



  author: John Mulligan <phlogistonjohn@yahoo.com>
  created: 2005-10-07
  licence: BSD-style  (see __licence_text__ @ bottom of source)
"""

__author__ = 'John Mulligan <phlogistonjohn@yahoo.com>'

__version__ = '2005.2'

__licence__ = "BSD-Style"



import xml.sax
import urllib

#these make up the base of the url
SCROB_WS_VERSION = '1.0'
SCROB_URL_ROOT = "http://ws.audioscrobbler.com"



_meta = """
topArtists;
topartists.xml;
ArtistHandler;
user;

Fetch the top artists for a user from last.fm.
Returns a list of dicts corresponding to metadata for each artist.

---

topTracks;
toptracks.xml;
TrackHandler;
user;

Fetch the top tracks for a user from last.fm.
Returns a list of dicts corresponding to metadata for each track.

---

recentTracks;
recenttracks.xml;
TrackHandler;
user;

Fetch the recently played tracks for a user from last.fm.
Returns a list of dicts corresponding to metadata for each track.

---

topAlbums;
topalbums.xml;
AlbumHandler;
user;

Fetch the top albums for  a user from last.fm.
Returns a list of dicts corresponding to metadata for each album.
Is there a bug in the XML in the image urls ?

---

weeklyArtistChart;
weeklyartistchart.xml;
ArtistHandler;
user;

Fetch the recent weekly artist chart for a user from last.fm.
Returns a list of dicts corresponding to metadata for each artist.

---

weeklyAlbumChart;
weeklyalbumchart.xml;
AlbumHandler;
user;

Fetch the recent weekly album chart for a user from last.fm.
Returns a list of dicts corresponding to metadata for each album.


---

weeklyTrackChart;
weeklytrackchart.xml;
TrackHandler;
user;

Fetch the recent weekly track chart for a user from last.fm.
Returns a list of dicts corresponding to metadata for each track.

---

friends;
friends.xml;
UserHandler;
user;

Fetch a user's friends.
Returns a list of dicts orresponding to metadata for each
last.fm user.

---

neighbors;
neighbours.xml;
UserHandler;
user;

Fetch a user's musical neighbors.
Returns a list of dicts orresponding to metadata for each
last.fm user.
---

---
neighbours;
neighbours.xml;
UserHandler;
user;

Fetch a user's musical neighbors.
Returns a list of dicts orresponding to metadata for each
last.fm user. 
Crazy people _over there_ spell neighbor wrong 8-)
---


profile;
profile.xml;
ProfileHandler;
user;

Fetch a user's profile information.
Retrusn a list with a single dictionary corresponding to
the selected user's profile.

---

topTags;
tags.xml;
TagHandler;
user;

Fetch the top tags for a user from last.fm.
Returns a list of dicts corresponding to metadata for each tag.

---

similar;
similar.xml;
ArtistHandler;
artist;

Fetch artists similar to the given artist name.
"""

_meta_incomplete = """
artist data
-----------

related artists

top fans

top tracks

top albums

top tags


tag data
--------

overall top tags

top artists

top albums

top tracks


group data
----------

weekly artist chart

weekly album chart

weekly




"""
















def parse_url( url, handlerClass ):
    """Opens a given url and parses the resulting XML.
    This xml should correspond to the audioscrobbler REST API.
    The actual parsing is done by the given handlerClass
    which should be a subclass of ScrobHandler.

    Returns the value given by calling handlerClass.results()
    after parsing is complete.
    """
    fio = urllib.urlopen( url )
    handler = handlerClass()
    parser = get_parser()

    parser.setContentHandler( handler )
    parser.parse( fio )

    return handler.results()





class ParsingError( Exception ):
    pass






class ScrobHandler( xml.sax.handler.ContentHandler ):
    """Base class for parsing XML from the Audioscrobbler REST API.
    This class implements most of a SAX handler object.

    Attributes from the last tag are stored in the attrs member variable.

    The data member variable holds a growing list of dictionaries that
    hold data for each item (track,artist,etc.)

    Subclasses should define
    ========================

    do_<tag> member function(s) which are executed when the parser hits
       a given tag

    field_states list/tuple, this loads the content into the current
    dictionary

    """



    debug = 0

    def __init__( self ):
        self.data = []
        self.stack = []
        self.state = ''


    def results(self):
        """Returns the parsed data.
        Re-implement this in a subclass to get more advanced/interesting
        return values from the functions.
        """
        return self.data


    def nextState( self, name ):
        """Saves the previous state, and sets self.state to name
        if name is true.
        Otherwise, retrive the previous state.
        """
        if name:
            name  =  str( name )
            self.stack.append( self.state )
            self.state = name
        else:
            try:
                self.state = self.stack.pop()
            except IndexError:
                self.state = ''


#    def skippedEntity( self, name ):
#        print 'HEHE', name


    def characters( self, content ):
        """Saves the data contained inside a tag if
        the given state is in the self.field_states list.
        """
        if self.state in self.field_states:
            if self.debug : print "CH(+)", content
            self.insert( self.state, content )


    def insert( self, name, data ):
        if name not in self.data[-1]:
            self.data[ -1 ][ name ]  = ''
   
        ok_data = self.prep_content( data )

        if type( ok_data ) in ( str, unicode ):
            self.data[ -1 ][ name ]  +=  ok_data 
        else:
            self.data[ -1 ][ name ] = ok_data


    def prep_content( self, content ):
        """Alters the raw XML data before saving it into the parsed data.
        The version does nothing, re-impl. in a sublcass
        if you need.
        """
        return content



    def startElement(self, tag, attributes ):
        """Sax parsing function.

        Generates a new state when entering a tag.
        """
        self.nextState( tag )
        self.attrs = attributes

        if hasattr( self, 'do_%s' % self.state ):
            getattr( self, 'do_%s' % self.state )()



    def endElement( self, tag ):
        """Sax parsing function"""
        self.nextState( None )



    def startDocument(self):
        """Sax parsing function"""
        self.data = []
        self.state = 'ready'



    def endDocument(self):
        """Sax parsing function"""
        pass


    def new_item( self ):
        self.data.append( dict() )





class TrackHandler( ScrobHandler ):
    """Class that implements parsing the AS-REST-API
    for track listings
    """

    def do_track( self ):
        """Update the data list.
        Create a new item for each new track found.
        """
        self.new_item()

    # fields that a track item contains
    field_states = ( 'artist', 'name', 'mbid', 'url', 'date', 'playcount',
                     'chartposition' )



class ArtistHandler( ScrobHandler ):
    """Class that implements parsing the AS-REST-API
    for artist listings
    """

    def do_artist( self ):
        """Update data list. Create a new item for
        each new artist found.
        """
        self.new_item()

    # fields that an artist item contains
    field_states = ( 'name', 'mbid', 'playcount', 'rank', 'url', 'chartposition' )




class TagHandler( ScrobHandler ):

    def do_tag( self ):
        self.new_item()

    field_states = ( 'name', 'count', 'url' )




class AlbumHandler( ScrobHandler ):
    """Class that implements parsing the AS-REST-API
    for album listings
    """

    def do_album( self ):
        self.new_item()


    def nextState( self, name ):
        if name and self.state == 'image':
            name =  self.state + '_' + name

        return ScrobHandler.nextState( self, name )


    field_states = ( 'name', 'mbid', 'artist', 'playcount', 'url', 'rank',
                     'image_large', 'image_medium', 'image_small', 'chartposition' )



class UserHandler( ScrobHandler ):

    def do_user( self ):
        self.new_item()
        self.insert( 'name', self.attrs[ 'username' ] )


    def do_connections( self ):
        self.insert( 'connections', list() )

    def insert( self, name, value ):
    
        if name == 'connection':
            value = self.prep_content( value )
            self.data[-1]['connections'].append( value )
            return

        return ScrobHandler.insert( self, name, value )


    def prep_content( self, data ):
        #if type(data) in ( list, tuple ):
        #    return ', '.join( data )
            
        return data

    field_states = ( 'name', 'url', 'connection', 'image', 'match' )




class ProfileHandler( ScrobHandler ):

    def do_profile( self ):
        self.new_item()
        self.insert( 'name', self.attrs[ 'username' ] )

    field_states = ( 'realname', 'url', 'mbox_sha1sum', 'playcount',
                     'registered', 'age', 'gender', 'country',  )




def get_parser():
    """Creates a sax parser object with sane defaults.
    This includes turning off some of the 'features'
    that slows parsing down.
    """

    parser = xml.sax.make_parser( )

    # these seem to vary machine-by-machine thats why i'm try:ing them
    try:
        parser.setFeature( xml.sax.handler.feature_validation, False )
    except:
        pass
    try:
        parser.setFeature( xml.sax.handler.feature_external_ges, False )
    except:
        pass
    try:
        parser.setFeature( xml.sax.handler.feature_external_pes, False )
    except:
        pass



        


    return parser



##########################################################################
#  Yeah, now were in the weird function generation stuff
#   its funky, very funky
##########################################################################


def _process( meta ):
    """Splits the function definition string up into sections.
    Converts the values if needed.
    And iterates over each section.
    """
    delim1 = '---'
    delim2 = ';'


    for section in meta.split(delim1) :
        #chop up the sections, clean up the edges
        section = section.strip()
        group = []

        if not section: continue #skip blank sections

        for ii,value in enumerate( section.split(delim2) ) :
            #divvy up sections, clean them.
            value = value.strip()

            #everything is strings, except for the handlerClass
            #convert it
            if ii == 2:
                value = getattr( scrobxlib , value )

            #add value to the list we're going to provide
            group.append( value )

        #right on red. yield to pedestrians
        yield group



def _autogenerate():
    """Uses processed function meta-data string to create functions.
    Uses the _basic_function_factory to most if its work
    """
    for node in _process( _meta ):
        if not node: continue
        #print node
        setattr( scrobxlib, node[0], _basic_function_factory( *node ) )


def _basic_function_factory( name, urlName, handlerClass, defl_type, doc=None ):
    """Generates a url-fetching & parsing function for AS-REST-API xml
    documents.
    """
    def scrob_fetch( target, target_type=defl_type ):
        #put the url together
        url = ( SCROB_URL_ROOT,
                SCROB_WS_VERSION,
                target_type,
                target,
                urlName
                )
        return parse_url( '/'.join(url), handlerClass )


    try:
        #works in python 2.4 ( *crosses fingers* )
        #in 2.3 __name__ cannot be changed
        scrob_fetch.__name__ = name
    except:
        pass

    #setup the docstring if we were passed it.
    if doc:
        scrob_fetch.__doc__ = doc


    #give it up for bob!
    return  scrob_fetch



#############################################################################
#       !!!!!!!! Important !!!!!!!!!!!!
# this actually _creates_ a bunch of very similar functions from
#  '_meta' variable defined at the top of the module

import scrobxlib # yay. this actually works
_autogenerate()


#############################################################################


__licence_text__ = """
Copyright (c) 2005, John Mulligan
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
Redistributions of source code must retain the above copyright notice, this
list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.
Neither the name of the John Mulligan nor the names of its contributors may
be used to endorse or promote products derived from this software without
specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
#my sister's dog is named tort...



