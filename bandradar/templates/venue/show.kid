<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <title>BandRadar - ${venue.name} Details</title>
</head>

<body>
    <div id="body">
        <h2>Venue: ${venue.name}</h2>
        <div id="details">
            <p py:if="venue.description">Description: ${venue.description}</p>
            <p py:if="venue.address">Address: ${venue.address}</p>
            <p py:if="venue.phone">Phone: ${venue.phone}</p>
            <p py:if="venue.url"><a href="${venue.url}">URL: ${venue.url}</a></p>
            <p py:if="not 'admin' in venue.added_by.groups">
            Added by: <a href="/users/${venue.added_by.user_name}">
                ${venue.added_by.user_name}</a></p>
            <p>Added: ${venue.get_fcreated()}</p>
            <p>Changed: ${venue.get_fupdated()}</p>
        </div>
        <h3>Past events</h3>
        <div class="event_list">
            <p py:for="e in past_events">
                ${e.get_fdate()}: <a href="/events/${e.id}">${e.name}</a>
            </p>
            <p py:if="not len(list(past_events))">None</p>
        </div>

        <h3>Upcoming events</h3>
        <div class="event_list">
            <p py:for="e in future_events">
                ${e.get_fdate()}: <a href="/events/${e.id}">${e.name}</a>
                ${e.time} ${e.cost}
            </p>
            <p py:if="not len(list(future_events))">None</p>
        </div>

        <div py:replace="edit_links(venue)" />
    </div>
</body>
</html>
