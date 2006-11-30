<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <title>BandRadar - Review Duplicates</title>
</head>

<body>
    <table>
    <tr py:for="e in events">
        <td>
            <a href="/events/${e.id}"><b py:strip="e.approved">${e.name}</b></a>
            <br />${e.date} ${e.time} <b>${e.cost}</b> ${e.ages}
        </td>
        <td>
            ${tg_ButtonWidget(action="/events/%d/edit" % e.id, label="Edit this event")}
        </td>
    </tr>
    </table>
</body>
</html>
