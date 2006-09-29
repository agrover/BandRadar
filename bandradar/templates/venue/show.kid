<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <title>BandRadar - ${venue.name} Details</title>
</head>

<body>
    <div id="body">
        <h2>Venue Details</h2>
        <p>${venue.name}</p>
        <p py:if="venue.description">Description: ${venue.description}</p>
        <p py:if="venue.address">Address: ${venue.address}</p>
        <p py:if="venue.phone">Phone: ${venue.phone}</p>
        <p py:if="venue.url">URL: ${venue.url}</p>

        <h3>Past events</h3>
        <div py:for="e in past_events">
            <p>${e.date.strftime("%x")}: <a href="/events/${e.id}">${e.name}</a> ${e.time} ${e.cost}</p>
        </div>

        <h3>Upcoming events</h3>
        <div py:for="e in future_events">
            <p>${e.date.strftime("%x")}: <a href="/events/${e.id}">${e.name}</a> ${e.time} ${e.cost}</p>
        </div>

        <div py:replace="edit_links(venue.id, 'venue')" />
    </div>
</body>
</html>
