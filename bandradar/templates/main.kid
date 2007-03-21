<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <title>BandRadar - Main</title>
</head>

<body>
    <div id="tagline">
        <h3>The easy way to track your favorite Portland bands!</h3>
        <ul>
            <li>Find out who's playing</li>
            <li>Get notified when bands you like play live</li>
            <li>Your band's gig not here? Add it!</li>
        </ul>
    </div>

    <div id="searchbox">
        <h2>Search Bands</h2>
        ${search_form(action="/artists/search")}
    </div>

    <hr />

    <h4>
        Tonight's events
        ${tg_ButtonWidget(action="/events/edit", label="Add a new event")}
    </h4>

    <p py:for="event_id, event_name, venue_name in events">
        <a href="/events/${event_id}">${event_name} @ ${venue_name}</a>
    </p>

    <h4>Top Tracked</h4>
    <p py:for="item in top_tracked">
        <a href="/artists/${item['id']}">${item['name']}</a>
    </p>

</body>
</html>
