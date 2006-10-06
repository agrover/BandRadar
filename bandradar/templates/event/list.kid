<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <title>BandRadar - Event List</title>
</head>

<body>
    <div id="searchbox">
        <h2>Search Events</h2>
        <?python from bandradar.events import event_search_form ?>
        ${event_search_form(action="/events/search")}
    </div>

    <h2>Event List (${count} for ${listby})</h2>
    Events:
    <a href="/events/list/today">Today</a>
    <a href="/events/list/tomorrow">Tomorrow</a>
    <a href="/events/list/yesterday">Yesterday</a>
    <a href="/events/list/week">Upcoming week</a>
    <a href="/events/list/all">All upcoming</a>

    <p py:for="e in events">
        <p><a href="/events/${e.id}">${e.name} @ ${e.venue.name}</a> ${e.get_fdate()} ${e.cost}</p>
    </p>

    <p>
        <a href="/events/edit">Add a new Event</a>
    </p>
</body>
</html>
