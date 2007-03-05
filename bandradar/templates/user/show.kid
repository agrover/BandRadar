<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <title>BandRadar - ${user.user_name} Details</title>
</head>

<body>
    <div id="userinfo">
        <h2>${user.user_name}</h2>
        <p>Since: ${user.created.strftime("%x")}</p>
        <p>Zip Code: ${user.zip_code}</p>
        <p>Website: <a href="${user.url}">${user.url}</a></p>
        <p>MySpace: <a py:if="user.myspace" href="http://myspace.com/${user.myspace}">
                http://myspace.com/${user.myspace}</a>
        </p>

        <p id="description" py:if="description">${XML(description)}</p>

        <div py:if="viewing_self">
            ${tg_ButtonWidget(action="/users/%s/edit" % user.user_name, label="Edit")}
        </div>

    </div>

    <h4>Bands Tracked: ${artists.count()}</h4>
    <table>
        <th>Band</th>
        <th>Events Performed</th>
        <th>Events Upcoming</th>
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

    <h4>Venues Tracked: ${venues.count()}</h4>
    <table>
        <th>Venue</th>
        <th>Past Events</th>
        <th>Upcoming Events</th>
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

    <h4>Attendances: ${attendances.count()}</h4>
    <table py:if="attendances.count()">
        <th>Event Name</th>
        <th>Date</th>
        <th>Comments</th>
        <tr py:for="att in attendances">
            <td>
                <a href="/events/${att.event.id}">${att.event.id}</a>
            </td>
            <td>
                ${att.date}
            </td>
            <td>
                ${att.comment}
            </td>
        </tr>
    </table>

</body>
</html>
