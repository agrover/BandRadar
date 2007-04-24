<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <title>BandRadar - ${user.user_name} Details</title>
</head>

<body>

    <div class="content">
        <h4>${user.user_name}</h4>
        <span py:if="viewing_self">
            ${tg_ButtonWidget(action="/users/%s/edit" % user.user_name, label="Edit")}
       </span>
       <div id="blurb">
       <p id="description" py:if="description">${XML(description)}</p>
       </div>
        <p><h5>Since:</h5> ${user.created.strftime("%x")}</p>
        <p><h5>Zip Code:</h5> ${user.zip_code}</p>
        <p><h5>Website:</h5> <a href="${user.url}">${user.url}</a></p>
        <p><h5>MySpace: </h5><a py:if="user.myspace" href="http://myspace.com/${user.myspace}">
                http://myspace.com/${user.myspace}</a>
       </p>
       
<!--
upcoming shows
tracked
related shows
bands
venues by-venue
venues by-date
-->
    <p><h5>Bands Tracked:</h5> ${artists.count()}</p>
    <div id="bandstracked">  
    <table py:if="artists.count()">
        <th>Band</th>
        <th>Performed</th>
        <th>Upcoming</th>
        <tr py:for="artist in artists">
            <td>
                <a href="/artists/${artist.id}">${artist.name}</a>
            </td>
            <td>
                ${artist.past_events.count()}
            </td>
            <td>
                ${artist.future_events.count()}
            </td>
        </tr>
    </table>
    </div>  
    
    <h5>Venues Tracked:</h5> ${venues.count()}
    <div id="venuestracked">   
    <table py:if="venues.count()">
        <th>Venue</th>
        <th>Past</th>
        <th>Upcoming</th>
        <tr py:for="venue in venues">
            <td>
                <a href="/venues/${venue.id}">${venue.name}</a>
            </td>
            <td>
                ${venue.past_events.count()}
            </td>
            <td>
                ${venue.future_events.count()}
            </td>
        </tr>
    </table>
    </div>

 
    <h5>Attendances:</h5> ${attendances.count()}
    <div id="attendance">    
    <table py:if="attendances.count()">
        <th>Event Name</th>
        <th>Date</th>
        <th>Comments</th>
        <tr py:for="att in attendances">
            <td>
                <a href="/events/${att.event.id}">${att.event.name}</a>
            </td>
            <td>
                ${att.event.date}
            </td>
            <td>
                ${att.comment}
            </td>
        </tr>
    </table>
    </div>
</div>


</body>
</html>
