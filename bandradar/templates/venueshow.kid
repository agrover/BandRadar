<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <title>BandRadar - ${v.name} Details</title>
</head>

<body>
    <div id="body">
        <h2>Venue Details</h2>
        <p>${v.name}</p>
        <p>Address: ${v.address}</p>
        <p>URL: ${v.url}</p>

        <div py:for="e in past_events">
            <p>${e.date}: <a href="/events/${e.id}">${e.name}</a> ${e.time} ${e.cost}</p>
        </div>

        <div py:for="e in future_events">
            <p><b>${e.date}: <a href="/events/${e.id}">${e.name}</a> ${e.time} ${e.cost}</b></p>
        </div>

        <div py:replace="edit_links(v.id, 'venue')" />
    </div>
</body>
</html>
