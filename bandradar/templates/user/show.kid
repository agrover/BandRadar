<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <title>BandRadar - ${user.user_name} Details</title>
</head>

<body>
    <div id="userinfo">
        <h2>${user.user_name}</h2>
        <p>${user.display_name}</p>
        <p>Since: ${user.created}</p>
        <p>Zip: ${user.zip_code}</p>
        <p>Website: <a href="${user.url}">${user.url}</a></p>

        <div py:if="viewing_self">
            <a href="/users/${user.user_name}/edit">Edit</a>
        </div>
    </div>

    <h4>Bands Tracked</h4>
    <p py:for="artist, before, after in art_list">
        <a href="/artists/${artist.id}">${artist.name}</a>
        <div>
            Past Events
            <p py:for="event in before">
                <a href="/events/${event.id}">${event.name}, ${event.venue.name},
                ${event.date}</a>
            </p>
        </div>
        <div>
            Upcoming Events
            <p py:for="event in after">
                <a href="/events/${event.id}">${event.name}, ${event.venue.name},
                ${event.date}</a>
            </p>
        </div>
    </p>

    <div py:replace="edit_links(user.user_name, 'user')" />
</body>
</html>
