<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <title>BandRadar - Band List</title>
</head>

<body>
    <div id="searchbox">
        <h2>Search all Bands</h2>
        <?python from bandradar.artists import artist_search_form ?>
        ${artist_search_form(action="/artists/search")}
    </div>

    <div id="list_title">
        Bands playing: ${listby} (${count})
        ${tg_ButtonWidget(action="/artists/edit", label="Add a new Band")}
    </div>
    <p><em>You will receive email when any tracked bands have shows added.</em>
    </p>
    <br />

    <div id="list_heading">
    With shows:
        <ul>
        <li><a href="/artists/list/today">Today</a></li>
        <li><a href="/artists/list/tomorrow">Tomorrow</a></li>
        <li><a href="/artists/list/yesterday">Yesterday</a></li>
        <li><a href="/artists/list/week">Upcoming week</a></li>
        <li><a href="/artists/list/all">All upcoming</a></li>
        </ul>
    </div>

    <table>
        <tr py:for="artist in artists">
            <td>${track_button(tracked=artist['is_tracked'], id=artist['id'], action="/artists/dyntrack")}
            </td>
            <td>
            <b py:strip="not artist['is_tracked']">
            <a href="/artists/${artist['id']}">${artist['name']}</a></b>
            </td>
        </tr>
    </table>
</body>
</html>
