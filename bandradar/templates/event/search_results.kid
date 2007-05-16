<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <title>BandRadar - Band List</title>
</head>

<body>
   <div class="content">

    <div id="searchbox">
        <h2>Search Events</h2>
        <?python from bandradar.events import event_search_form ?>
        ${event_search_form(action="/events/search")}
    </div>
<br clear="all"></br>
    <h5>Event Search Results</h5>
    <p py:for="e in events">
        <p><b><a href="/events/${e.id}">${e.name}</a></b> ${e.date}</p>
    </p>
</div>
</body>
</html>
