<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <title>BandRadar - Event List</title>
</head>

<body>
    <div id="searchbox">
        <h2>Search Events</h2>
        <?python from bandradar.artists import artist_search_form ?>
        ${event_search_form(action="/events/search")}
    </div>

    <h2>Event List</h2>

    <p py:for="e in events">
        <p><a href="/events/${e.id}">${e.name}</a> ${e.date} ${e.cost}</p>
    </p>

    <p>
        <a href="/events/edit">Add a new Event</a>
    </p>
</body>
</html>
