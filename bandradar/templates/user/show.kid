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
        <p>Since: ${user.created.strftime("%x")}</p>
        <p>Zip Code: ${user.zip_code}</p>
        <p>Website: <a href="${user.url}">${user.url}</a></p>
        <p>More info: ${user.description}</p>

        <div py:if="viewing_self">
            <a href="/users/${user.user_name}/edit">Edit</a>
        </div>

    </div>

    <h4>Bands Tracked</h4>
    <p py:for="artist, old, new in art_list">
        <a href="/artists/${artist.id}">${artist.name}</a> (${old} performed,
        ${new} upcoming)
    </p>

</body>
</html>
