<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <title>BandRadar - ${user.user_name} Details</title>
</head>

<body>
    <div id="userinfo">
        <h2>${user.user_name}</h2>
        <p>Since: ${user.created.strftime("%x")}</p>
        <p>Zip Code: ${user.zip_code}</p>
        <p>Website: <a href="${user.url}">${user.url}</a></p>
        <p>MySpace: <a py:if="user.myspace" href="http://myspace.com/${user.myspace}">
                http://myspace.com/${user.myspace}</a>
        </p>

        <p id="description" py:if="description">${XML(description)}</p>

        <div py:if="viewing_self">
            ${tg_ButtonWidget(action="/users/%s/edit" % user.user_name, label="Edit")}
        </div>

    </div>

    <h4>Bands Tracked: ${len(art_list)}</h4>
    <table>
        <th>Band</th>
        <th>Events Performed</th>
        <th>Events Upcoming</th>
        <tr py:for="name, id, old, new in art_list">
            <td>
                <a href="/artists/${id}">${name}</a>
            </td>
            <td>
                ${old}
            </td>
            <td>
                ${new}
            </td>
        </tr>
    </table>
</body>
</html>
