<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <title>BandRadar - ${event.name} Details</title>
</head>

<body>
    <div class="content">
     <div class="mapright">
        ${googlemap(venue=event.venue, width=250, height=200)}
</div>
<h4>${event.name}
             <span py:if="is_tracked">${tg_ButtonWidget(action="/events/%s/untrack?viewing=yes" % event.id, label="Untrack")}
     </span>
     <span py:if="not is_tracked">${tg_ButtonWidget(action="/events/%s/track?viewing=yes" % event.id,     label="Track")}</span>
        <span py:if="event.ticket_url">${tg_ButtonWidget(action=event.ticket_url, label="Buy Tickets")}</span>      

     
</h4>
   <div id="blurb">
        <p id="description" py:if="description">${XML(description)}</p>
  </div>    
            <p><h5>Date:</h5> ${event.date.strftime("%x")}</p>
            <p py:if="event.time"><h5>Time:</h5> ${event.time}</p>
            <p py:if="event.cost"><h5>Cost:</h5> ${event.cost}</p>
            <p py:if="event.ages"><h5>Ages:</h5> ${event.ages}</p>
            <p py:if="event.url"><h5>Website:</h5> <a href="${event.url}">${event.url}</a></p>
            <p><h5>Where:</h5> <a href="/venues/${event.venue.id}">${event.venue.name}</a>
                <span id="address" py:if="event.venue.address">(${event.venue.address})</span>
            </p>
            <p><h5>With:</h5>  ${artist_list(artists=event.artists)}</p>
            <p py:if="not 'admin' in event.added_by.groups">
            <h5>Added by:</h5> <a href="/users/${event.added_by.user_name}">
                ${event.added_by.user_name}</a></p>
            <p><h5>Added:</h5> ${event.fcreated}</p>
            <p><h5>Changed:</h5> ${event.fupdated}</p>
            <br></br>
            <br></br>
           
        <div py:if="'admin' in tg.identity.groups and event.sources.count()">
            From: ${",".join([s.name for s in event.sources])}
        </div>

        <div py:replace="edit_links(event)" />

 </div>
</body>
</html>
