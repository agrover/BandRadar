<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <title>BandRadar - Venue List</title>
</head>

<body>
  <div class="content">
   <div id="help">When you track a venue, BandRadar sends you a weekly email with upcoming events.</div>   
    <div id="searchbox">
        <h3>Search all Venues</h3>
        <?python from bandradar.venues import venue_search_form ?>
        ${venue_search_form(action="/venues/search")}
    </div>
 
    

   <div id="venue">
    <table>
    <h5>Venues with upcoming events
        <span py:if="'admin' in tg.identity.groups">
            ${tg_ButtonWidget(action="/venues/edit", label="Add a new venue")}
        </span>
    </h5>
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
</body>
</html>
