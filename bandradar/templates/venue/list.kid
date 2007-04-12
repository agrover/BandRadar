<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <title>BandRadar - Venue List</title>
</head>

<body>
    <div class="topContainer">
      <div id="wrapper">     
      <div class="contentArea">
    <div id="searchbox">
        <h2>Search all Venues</h2>
        <?python from bandradar.venues import venue_search_form ?>
        ${venue_search_form(action="/venues/search")}
    </div>

    <div id="list_title">
    </div>

    <h3>Venues with upcoming events
        <span py:if="'admin' in tg.identity.groups">
            ${tg_ButtonWidget(action="/venues/edit", label="Add a new venue")}
        </span>
    </h3>
    <p><em>You will receive a weekly email with upcoming events at any tracked venues.</em>
    </p>
    <br />
    <table>
    <tr py:for="v in venues">
        <td>
            <a href="/venues/${v['id']}">${v['name']}</a>
            <span py:if="v['eventcount']"> (${v['eventcount']} upcoming)</span>
        </td>
        <td>
            ${tg_track_button(tracked=v['id'] in tracked_venues, id=v['id'], action="/venues/dyntrack")}
        </td>
    </tr>
    </table>
    </div>
    </div>
    </div>
</body>
</html>
