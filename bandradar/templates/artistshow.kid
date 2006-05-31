<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <title>BandRadar - ${artist.name} Details</title>
</head>

<body>
    <?python from turbogears import identity ?>
    <div id="body">
        <h2>Band Details</h2>
        <p>${artist.name}</p>
        <p>${artist.description}</p>
        <p py:if="artist.added_by">Added by: ${artist.added_by.user_name}</p>
        <p py:if="is_tracked">
            <i>currently being tracked by you.</i>
            <a href="/artists/${artist.id}/untrack?viewing=yes">Untrack</a>
        </p>
        <p py:if="not is_tracked">
            <i>not currently tracked by you.</i>
            <a href="/artists/${artist.id}/track?viewing=yes">Track</a>
        </p>

        <h4>Events</h4>
        <span py:if="identity.current.user">(Know of an upcoming event not listed? <a href="/events/edit?artist_prefill=${artist.id}">Add it</a>!)</span>
        <p py:for="event in events">
            <a href="/events/${event.id}">${event.name}</a> @ 
            <a href="/venues/${event.venue.id}">${event.venue.name}</a>
        </p>

        <div py:replace="edit_links(artist.id, 'artist')" />
    </div>
</body>
</html>
