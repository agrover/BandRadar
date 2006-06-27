<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <title>BandRadar - Band List</title>
</head>

<body>
    <div id="searchbox">
        <h2>Search Bands</h2>
        <?python from bandradar.artists import artist_search_form ?>
        ${artist_search_form(action="/artists/search")}
    </div>

    <h2>Band List</h2>
    With shows:
    <a href="/artists/list/today">Today</a>
    <a href="/artists/list/tomorrow">Tomorrow</a>
    <a href="/artists/list/yesterday">Yesterday</a>
    <a href="/artists/list/week">This week</a>
    <br />
    Sort:
    <a href="/artists/list/top">Most Popular</a>
    <a href="/artists/list/top">By Name</a>

    <p py:for="a in artists">
        <p><b py:strip="not a['is_tracked']"><a href="/artists/${a['id']}">${a['name']}</a></b></p>
    </p>

    <p>
        <a href="/artists/edit">Add a new Band</a>
    </p>
</body>
</html>
