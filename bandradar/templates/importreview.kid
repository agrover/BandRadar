<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <title>BandRadar - Imported Show List</title>
</head>

<body>
    <h2>Review New Shows (${shown} of ${total})</h2>

    <form action="/importers/reviewsubmit" method="post">
        <input type="submit" name="submit" value="Import Checked" />
        <input type="submit" name="submit" value="Delete Checked" />
        <?python e_counter = 0 ?>
        <table>
        <tr py:for="e in events">
            <td>
                <input py:attrs="type='checkbox', name='accept%s' % e.id, checked='true'" />
            </td>
            <td>
                <input py:attrs="type='hidden', name='eid' + str(e_counter), value=e.id" />
                <a href="/events/${e.id}/edit">
                    <b py:strip="e.verified">${e.name}</b>
                </a>
            </td>
            <td>
                <div py:for="artist in e.artists">
                    <a href="/artists/${artist.id}/edit">
                        <b py:strip="artist.verified">${artist.name}</b>
                    </a>
                </div>
            </td>
            <td>
                <a href="/venues/${e.venue.id}/edit">
                    <b py:strip="e.venue.verified">${e.venue.name}</b><br />
                </a>
                ${e.date} ${e.time} ${e.cost}
            </td>
            <?python e_counter += 1 ?>
        </tr>
        </table>
        <input type="submit" name="submit" value="Import Checked" />
        <input type="submit" name="submit" value="Delete Checked" />
    </form>
    <a href="/importers/reviewpurge">Remove all entries</a>
</body>
</html>
