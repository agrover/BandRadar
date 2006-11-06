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
        <?python from bandradar import WWBL ?>
        <tr py:for="e in events">
        
            <td>
                <a href="${WWBL.date_to_url(e.date)}">Link</a>
            </td>
            <td>
                <input py:attrs="type='checkbox', name='accept%s' % e.id, checked='true'" />
            </td>
            <td>
                <input py:attrs="type='hidden', name='eid' + str(e_counter), value=e.id" />
                <a href="/events/${e.id}/edit"><b py:strip="e.approved">${e.name}</b></a>
                <br />${e.date} ${e.time} ${e.cost} ${e.ages}
            </td>
            <td>
                <div py:for="artist in e.artists">
                    <a href="/artists/${artist.id}/edit">
                        <b py:strip="artist.approved">${artist.name}</b>
                    </a>
                </div>
            </td>
            <td>
                <a href="/venues/${e.venue.id}/edit">
                    <b py:strip="e.venue.approved">${e.venue.name}</b><br />
                </a>
                ${e.venue.address} ${e.venue.phone}
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
