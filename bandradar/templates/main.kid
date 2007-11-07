<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <title>BandRadar - Main</title>
</head>

<body>

 <div class="content">   
 
  <div class="leftcontent">

 <div id="tagline">
   <p>Track your favorite artists and venues! Get notified when new events come to town. blahahahahahahahah.</p>  
  </div>
  

<div id="navcontainer">
 <ul id="navlist">
 <li id="login"><span py:if="not tg.identity.user">
            <a href="/users/login">Come In!</a>
        </span>
        <span py:if="tg.identity.user">
            <a href="/users/${tg.identity.user.user_name}">
           ${tg.identity.user.user_name}'s Page</a>
        </span></li>
        
        <li id="nav-bands"><a href="/artists/list">Bands</a></li>
        <ul id="subnavlist">
        <li id="subactive"><a href="/artists/edit" id="subcurrent">Add a Band</a></li>
        </ul>        
        <li id="nav-events"><a href="/events/list">Events</a></li>
        <ul id="subnavlist">
        <li id="subactive"><a href="/events/edit" id="subcurrent">Add an Event</a></li>
        </ul>
       
        <li id="nav-venues"><a href="/venues/list">Venues</a></li>
        <ul id="subnavlist">
        <li id="subactive"><a href="/events/edit" id="subcurrent">Add a Venue</a></li>
        </ul>
        
        <li id="nav-logout"><span py:if="tg.identity.user">
           <a href="/users/logout">Logout</a>
        </span></li>
        </ul>
       </div>
 </div>  
  
  <div class="centercontent">
  
  <div id="banner">
	<a href="/"><img src="/static/images/banner.png" alt="BandRadar logo" /></a>
    </div>
 
    <div id="tonight">
     	<ul>
        <li py:for="event_id,event_name,venue_name in events">
    	<a href="/events/${event_id}"><b>${venue_name}</b>:  ${event_name}</a></li>
    	</ul>
    </div>	 
    
  </div>       
	
  
 <div class="rightcontent">
   ${tg_global_search_form(action="/artists/search")}

       
     <div id="sitestats">
	    <div id="bandstats">    
        <h5>Top Tracked Bands</h5>
        <p py:for="item in top_artists">
        <a href="/artists/${item['id']}">${item['name']}</a></p>
        </div>        
        <div id="eventstats">
        <h5>Top Tracked Events</h5>
        <p py:for="item in top_events">
        <a href="/events/${item['id']}">${item['name']}</a></p>
        </div>     
        <div id="venuestats">    
        <h5>Top Tracked Venues</h5>
        <p py:for="item in top_venues">
        <a href="/venues/${item['id']}">${item['name']}</a></p>
        </div>	
        </div>
               
         </div>  
  
 </div>

</body>
</html>
