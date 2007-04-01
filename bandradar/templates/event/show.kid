<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <title>BandRadar - ${event.name} Details</title>
</head>

<body>
    <div id="body">

        ${googlemap(venue=event.venue, width=250, height=200)}

        <h2>Event: ${event.name}</h2>

        <div id="details">
            <p id="description" py:if="description">${XML(description)}</p>
            <p>Date: ${event.date.strftime("%x")}</p>
            <p py:if="event.time">Time: ${event.time}</p>
            <p py:if="event.cost">Cost: ${event.cost}</p>
            <p py:if="event.ages">Ages: ${event.ages}</p>
            <p py:if="event.url">Website: <a href="${event.url}">${event.url}</a></p>
            <p>Where: <a href="/venues/${event.venue.id}">${event.venue.name}</a>
                <span id="address" py:if="event.venue.address">(${event.venue.address})</span>
            </p>
            With: ${artist_list(artists=event.artists)}
            <p py:if="not 'admin' in event.added_by.groups">
            Added by: <a href="/users/${event.added_by.user_name}">
                ${event.added_by.user_name}</a></p>
            <p>Added: ${event.fcreated}</p>
            <p>Changed: ${event.fupdated}</p>
            <div py:if="is_tracked">
                <i>currently being tracked by you.</i>
                ${tg_ButtonWidget(action="/events/%s/untrack?viewing=yes" % event.id, label="Untrack")}
            </div>
            <div py:if="not is_tracked">
                <i>not currently tracked by you.</i>
                ${tg_ButtonWidget(action="/events/%s/track?viewing=yes" % event.id, label="Track")}
            </div>

        </div>

        <div py:if="'admin' in tg.identity.groups and event.sources.count()">
            From: ${",".join([s.name for s in event.sources])}
        </div>

        <div py:replace="edit_links(event)" />

    </div>
</body>
</html>
