<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <title>BandRadar - ${venue.name} Details</title>
</head>

<body>
    <div id="body">

        ${googlemap(width=250, height=200)}

        <h2>Venue: <span id="name">${venue.name}</span></h2>
        <div id="details">
            <p id="description" py:if="description">${XML(description)}</p>
            <p py:if="venue.address">Address: <span id="address">${venue.address}</span></p>
            <p py:if="venue.phone">Phone: <span id="phone">${venue.phone}</span></p>
            <p py:if="venue.url">Website: <a href="${venue.url}">${venue.url}</a></p>
            <p py:if="venue.myspace">MySpace:
                <a href="http://myspace.com/${venue.myspace}">
                    http://myspace.com/${venue.myspace}</a>
            </p>
            <p py:if="not 'admin' in venue.added_by.groups">
            Added by: <a href="/users/${venue.added_by.user_name}">
                ${venue.added_by.user_name}</a></p>
            <p>Added: ${venue.get_fcreated()}</p>
            <p>Changed: ${venue.get_fupdated()}</p>
            <p py:if="tracked_count">Users tracking: ${tracked_count}</p>
            <div py:if="is_tracked">
                <i>Currently being tracked by you. You will receive weekly emails with
                upcoming shows for this venue.</i>
                ${tg_ButtonWidget(action="/venues/%s/untrack?viewing=yes" % venue.id, label="Untrack")}
            </div>
            <div py:if="not is_tracked">
                <i>not currently tracked by you.</i>
                ${tg_ButtonWidget(action="/venues/%s/track?viewing=yes" % venue.id, label="Track")}
            </div>

        </div>
        <h3>Past events</h3>
        <div class="event_list">
            <p py:for="e in past_events">
                ${e.get_fdate()}: <a href="/events/${e.id}">${e.name}</a>
            </p>
            <p py:if="not len(list(past_events))">None</p>
        </div>

        <h3>Upcoming events</h3>
        <div class="event_list">
            <p py:for="e in future_events">
                ${e.get_fdate()}: <a href="/events/${e.id}">${e.name}</a>
                ${e.time} ${e.cost}
            </p>
            <p py:if="not len(list(future_events))">None</p>
        </div>

        <div py:replace="edit_links(venue)" />
    </div>
</body>
</html>
