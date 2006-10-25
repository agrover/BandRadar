<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <title>BandRadar - ${artist.name} Details</title>
</head>

<body>
    <?python from turbogears import identity ?>
    <div id="body">
        <p class="name">${artist.name}</p>
        <p>${artist.description}</p>
        <p py:if="not 'admin' in artist.added_by.groups">
        Added by: <a href="/users/${event.added_by.user_name}">
            ${artist.added_by.user_name}</a></p>
        <p>Added: ${artist.get_fcreated()}</p>
        <p>Changed: ${artist.get_fupdated()}</p>
        <p py:if="tracked_count">Users tracking: ${tracked_count}</p>
        <div py:if="is_tracked">
            <i>currently being tracked by you.</i>
            ${tg_ButtonWidget(action="/artists/%s/untrack?viewing=yes" % artist.id, label="Untrack")}
        </div>
        <div py:if="not is_tracked">
            <i>not currently tracked by you.</i>
            ${tg_ButtonWidget(action="/artists/%s/track?viewing=yes" % artist.id, label="Track")}
        </div>

        <div id="list_title">
            Events
            <span py:if="identity.current.user">
                ${tg_ButtonWidget(action="/events/edit?artist_prefill=%s" % artist.id, label="Add a new event")}
            </span>
        </div>
        <p py:for="event in events">
            ${event.get_fdate()}:
            <a href="/events/${event.id}">${event.name}</a> @ 
            <a href="/venues/${event.venue.id}">${event.venue.name}</a>
        </p>

        <div py:replace="edit_links(artist)" />
    </div>
</body>
</html>
