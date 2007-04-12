<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <title>BandRadar - ${user.user_name} Details</title>
</head>

<body>
 <div class="topContainer">
      <div id="wrapper">     
      <div class="contentArea">

    <div id="userinfo">
        <h2>${user.user_name}</h2>
        <p>Since: ${user.created.strftime("%x")}</p>
        <p>Zip Code: ${user.zip_code}</p>
        <p>Website: <a href="${user.url}">${user.url}</a></p>
        <p>MySpace: <a py:if="user.myspace" href="http://myspace.com/${user.myspace}">
                http://myspace.com/${user.myspace}</a>
        </p>

        <div py:if="viewing_self">
            ${tg_ButtonWidget(action="/users/%s/edit" % user.user_name, label="Edit")}
        </div>

    </div>
<!--
upcoming shows
tracked
related shows
bands
venues by-venue
venues by-date
-->
    <h4>Bands Tracked: ${artists.count()}</h4>
    <table>
        <th>Band</th>
        <th>Events Performed</th>
        <th>Events Upcoming</th>
        <th>Similar Bands</th>
        <tr py:for="artist in artists">
            <td>
                <a href="/artists/${artist.id}">${artist.name}</a>
            </td>
            <td>
                ${artist.past_events.count()}
            </td>
            <td>
                ${artist.future_events.count()}
            </td>
            <td>
                ${artist_list(artists=artist.similars)}
            </td>
        </tr>
    </table>

</div>
</div>
</div>
</body>
</html>
