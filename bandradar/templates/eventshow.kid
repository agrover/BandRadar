<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <title>BandRadar - ${event.name} Details</title>
</head>

<body>
    <div id="body">
        <h2>Event Details</h2>
        <p>${event.name}</p>
        <p>Description: ${event.description}</p>
        <p>Date: ${event.date}</p>
        <p>Time: ${event.time}</p>
        <p>Cost: ${event.cost}</p>
        <p>Ages: ${event.ages}</p>
        <p>Website: ${event.url}</p>
        <p>Where: <a href="/venues/${event.venue.id}">${event.venue.name}</a></p>
        With:
        <span py:replace="XML(artisthtml)"></span>
        <p>Added: ${event.created}</p>
        <p py:if="event.added_by">Added By: ${event.added_by}</p>

        <div py:replace="edit_links(event.id, 'event')" />
    </div>
</body>
</html>
