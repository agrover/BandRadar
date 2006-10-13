<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <title>BandRadar - Main</title>
</head>

<body>
    <p id="tagline">Portland's easy way to track your favorite bands!</p>

    <div id="searchbox">
        <?python from bandradar.artists import artist_search_form ?>
        ${artist_search_form(action="/artists/search")}
    </div>

    <h5>Tonight's events</h5>

    <p py:for="event in events">
        <a href="/events/${event.id}">${event.name} @ ${event.venue.name}</a>
    </p>

</body>
</html>
