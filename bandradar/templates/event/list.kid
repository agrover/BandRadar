<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <title>BandRadar - Event List</title>
</head>

<body>
    <div id="searchbox">
        <h2>Search all Events</h2>
        ${event_search_form(action="/events/search")}
    </div>

    <div id="list_title">
        Events: ${listby} (${count})
        ${tg_ButtonWidget(action="/events/edit", label="Add a new event")}
    </div>

    <div id="list_heading">
    With shows:
        <ul>
        <li><a href="/events/list/today">Today</a></li>
        <li><a href="/events/list/tomorrow">Tomorrow</a></li>
        <li><a href="/events/list/yesterday">Yesterday</a></li>
        <li><a href="/events/list/week">Upcoming week</a></li>
        <li><a href="/events/list/all">All upcoming</a></li>
        </ul>
    </div>

    <table>
        <tr py:for="event_id, event_name, event_date, venue_name, is_tracked in events">
            <td>
                <a href="/events/${event_id}">${event_name} @ ${venue_name}</a>
            </td>
            <td>
                ${event_date}
            </td>
            <td>
                ${track_button(tracked=is_tracked, id=event_id, action="/events/dyntrack")}
            </td>
        </tr>
    </table>
</body>
</html>
