<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <title>BandRadar - ${venue.name} Details</title>
</head>

<body>
           
           
          <span id="name"><h4>${venue.name}</h4></span>
          &nbsp;
          <span py:if="is_tracked">
                ${tg_ButtonWidget(action="/venues/%s/untrack?viewing=yes" % venue.id, label="Untrack")}</span>
          
          <span py:if="not is_tracked">
             ${tg_ButtonWidget(action="/venues/%s/track?viewing=yes" % venue.id, label="Track")}
          </span>
          <span py:if="'admin' in tg.identity.groups">
            <form class="buttonform" action="/venues/${venue.id}/merge" method="POST">
                <label style="font-size: x-small;font-weight: normal" for="other_id">Merge into:</label>
                <input type="text" id="other_id" name="other_id" size="8"/>
                <input type="submit" class="button" value="Merge"/>
            </form>
          </span>

          
      <li></li>       
            <div id="blurb">   
                    
            <p id="description" py:if="description">${XML(description)}</p>
             ${googlemap(venue=venue, width=250, height=200)} 
            </div>           
            <p py:if="venue.address"><h5>Address: </h5><span id="address">${venue.address}</span></p>
            <p py:if="venue.phone"><h5>Phone: </h5><span id="phone">${venue.phone}</span></p>
          
            <p py:if="venue.url"><h5>Website: </h5><a href="${venue.url}">${venue.url}</a></p>
            <p py:if="venue.myspace"><h5>MySpace:</h5>
                <a href="http://myspace.com/${venue.myspace}">
                    http://myspace.com/${venue.myspace}</a>
            </p>
            <p py:if="not 'admin' in venue.added_by.groups">
            Added by: <a href="/users/${venue.added_by.user_name}">
                ${venue.added_by.user_name}</a></p>
            <p><h5>Added: </h5>${venue.fcreated}</p>
            <p><h5>Changed: </h5>${venue.fupdated}</p>
             <p py:if="tracked_count"><h5>Users tracking: </h5>${tracked_count}</p>
                       
         <div id="upcoming">
             <p><h5>Upcoming events:</h5></p>
             <table>
                <colgroup>
                <col id="when"/>
                <col id="who"/> 
                </colgroup>
                <thead>
                <tr>
                <th when ="col">When</th>
                <th who ="col">Who</th>              
                </tr>   
                </thead>      
               <tbody>                      
                 <tr py:for="e in future_events">
                 <td class="when"><a href="/events/${e.id}">${e.fdate}&nbsp;&nbsp;${e.time}</a></td>
                 <td class="who"><a href="/events/${e.id}">${e.name}</a></td>
                 </tr>
                 </tbody>               
           </table>
        <p py:if="not len(list(future_events))">None</p>
        <br clear="all"></br>
        </div>       
       
        <div id="past">
           <h5> Past events (<a href="?list_all=1">See all</a>)</h5>
           <table>
              <colgroup>
              <col id="when"/>
              <col id="who"/> 
              </colgroup>
               <thead>
                 <tr>
                 <th when ="col">When</th>
                 <th who ="col">Who</th>              
                 </tr>   
               </thead>      
               <tbody> 
               <tr py:for="e in past_events">
               <td class="when"> <a href="/events/${e.id}">${e.fdate}</a></td>
               <td class="who"> <a href="/events/${e.id}">${e.name}</a></td>
               </tr>
               </tbody>             
        </table>            
            <p py:if="not len(list(past_events))">None</p>
        </div>
              
           ${tg_ButtonWidget(action="/events/edit?venue_prefill=%s" % venue.id, label="Add a new event")}

        <div py:replace="edit_links(venue)"/>
       
</body>
</html>
