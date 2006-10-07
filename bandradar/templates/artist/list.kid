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

    <h2>Band List (${count} for ${listby})</h2>
    With shows:
    <a href="/artists/list/today">Today</a>
    <a href="/artists/list/tomorrow">Tomorrow</a>
    <a href="/artists/list/yesterday">Yesterday</a>
    <a href="/artists/list/week">Upcoming week</a>
    <a href="/artists/list/all">All upcoming</a>

    <table>
        <tr py:for="artist in artists">
            <td>
                <a py:if="artist['is_tracked']" href="/artists/${artist['id']}/untrack">Untrack</a>
                <a py:if="not artist['is_tracked']" href="/artists/${artist['id']}/track">Track</a>
            </td>
            <td>
            <b py:strip="not artist['is_tracked']">
            <a href="/artists/${artist['id']}">${artist['name']}</a></b>
            </td>
        </tr>
    </table>
    <p>
        <a href="/artists/edit">Add a new Band</a>
    </p>
</body>
</html>
