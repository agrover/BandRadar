<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <title>BandRadar - Main</title>
</head>

<body>

	 
     <div class="content"> 
     <div id="searchbox">
      <h3>Search all Bands</h3>
        ${search_form(action="/artists/search")}
        <?python from bandradar.artists import artist_search_form ?> 
     </div>    
                
      <div class="rightcontent">
        <h3>Tonight</h3>
     	<small><p py:for="event_id, event_name, venue_name in events">
    	<a href="/events/${event_id}"><b>${event_name}</b>@${venue_name}</a>
    	</p></small> 
       </div>	              
     
    <div id="tagline">
              <h1>The easy way to track your favorite Portland bands!</h1>
                <p>Always missing your favorite <a href="/artists/list"> band's</a> gig? Sign in to be alerted <a href="/events/list"> when</a> and <a href="/venues/list"> where</a> they play next.  Oh and you can also track that <a href="/venues/list"> bar</a> with the live music seeping out that you keep walking by on your way home. In a <a href="/artists/list"> band</a> not on BandRadar? Add your name to the artist list to let your fans know a gig is upcoming.</p>
                <p>A special note to our friends running IE: Ok we know there are some issues especially on the pages with the maps. Working on them. In the meantime you could give Firefox a whirl!</p>
     
   </div> 
     
     <div id="bandstats">    
        <p><h5>Top Tracked Bands</h5></p>
        <span py:for="item in top_artists">
        <a href="/artists/${item['id']}">${item['name']}</a></span>
     </div>
   
     <div id="venuestats">    
        <p><h5>Top Tracked Venues</h5>
        <span py:for="item in top_venues">
        <a href="/venues/${item['id']}">${item['name']}</a></span>
        </p>
     </div>		
     
     <div id="eventstats">
     <p><h5>Top Tracked Events</h5></p>
     <span py:for="item in top_events">
        <a href="/events/${item['id']}">${item['name']}</a></span>
     </div>
     </div>          
                

 </body>
</html>
