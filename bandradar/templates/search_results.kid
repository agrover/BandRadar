<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <title>BandRadar - Venue List</title>
</head>

<body>
    <h5>Venue Search Results</h5>
    <p py:if="not venues.count()">
        None
    </p>
    <div py:if="venues.count()">
        <p py:for="v in venues">
            <a href="/venues/${v.id}">${v.name}</a>
        </p>
    </div>
    <h5>Artist Search Results</h5>
    <p py:if="not artists.count()">
        None
    </p>
    <div py:if="artists.count()">
        <p py:for="a in artists">
             <a href="/artists/${a.id}">${a.name}</a>
        </p>
    </div>

</body>
</html>
