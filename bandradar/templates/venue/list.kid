<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <title>BandRadar - Venue List</title>
</head>

<body>
    <div id="searchbox">
        <h2>Search Venues</h2>
        <?python from bandradar.venues import venue_search_form ?>
        ${venue_search_form(action="/venues/search")}
    </div>

    <h2>Venue List</h2>

    <p py:for="v in venues">
        <p>
            <a href="/venues/${v.id}">${v.name}</a>
            <span py:if="v.eventcount"> (${v.eventcount} upcoming)</span>
        </p>
    </p>

    <p>
        <a href="/venues/edit">Add a new venue</a>
    </p>
</body>
</html>
