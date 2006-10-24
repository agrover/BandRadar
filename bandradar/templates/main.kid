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
        <?python from bandradar.artists import artist_search_form ?>
        ${artist_search_form(action="/artists/search")}
    </div>

    <hr />

    <h4>Tonight's events</h4>

    <p py:for="event in events">
        <a href="/events/${event.id}">${event.name} @ ${event.venue.name}</a>
    </p>

</body>
</html>
