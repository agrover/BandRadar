<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <title>BandRadar - ${event.name} Details</title>
</head>

<body>
    <div id="body">
        <h2>Event Details</h2>
        <p>${event.name}</p>
        <p py:if="event.description">Description: ${event.description}</p>
        <p>Date: ${event.date.strftime("%x")}</p>
        <p py:if="event.time">Time: ${event.time}</p>
        <p py:if="event.cost">Cost: ${event.cost}</p>
        <p py:if="event.ages">Ages: ${event.ages}</p>
        <p py:if="event.url">Website: <a href="${event.url}">${event.url}</a></p>
        <p>Where: <a href="/venues/${event.venue.id}">${event.venue.name}</a>
            <span py:if="event.venue.address">(${event.venue.address})</span>
        </p>
        With:
        <span py:replace="XML(artisthtml)"></span>
        <p>Added: ${event.created.strftime("%x %X")}</p>
        <p py:if="event.added_by">Added By: ${event.added_by.user_name}</p>

        <div py:replace="edit_links(event.id, 'event')" />
    </div>
</body>
</html>
