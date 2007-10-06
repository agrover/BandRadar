<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <title>BandRadar - ${artist.name} Details</title>
</head>

<body>
    <div class="content">
        <p class="name"><h4>${artist.name}</h4>&nbsp;&nbsp;
        <span py:if="is_tracked">${tg_ButtonWidget(action="/artists/%s/untrack?viewing=yes" % artist.id, label="Untrack")}</span>
        <span py:if="not is_tracked">${tg_ButtonWidget(action="/artists/%s/track?viewing=yes" % artist.id, label="Track")}</span>
        <span py:if="'admin' in tg.identity.groups">
            ${tg_ButtonWidget(action="/artists/%s/split" % artist.id, label="Split")}
            <form class="buttonform" action="/artists/${artist.id}/merge" method="POST">
                <label style="font-size: x-small;font-weight: normal" for="other_id">Merge into:</label>
                    <input type="text" id="other_id" name="other_id" size="8"/>
                    <input type="submit" class="button" value="Merge"/>
            </form>
        </span>
        <div id="blurb">
            <p id="description" py:if="description">${XML(description)}</p>
        </div>    
        <p py:if="artist.url"><h5>Website: </h5><a href="${artist.url}">${artist.url}</a></p>
        <p py:if="artist.myspace"><h5>MySpace:</h5>
            <a href="http://myspace.com/${artist.myspace}">
                http://myspace.com/${artist.myspace}</a>
        </p>

        <p py:if="not 'admin' in artist.added_by.groups">
        <h5>Added by:</h5><a href="/users/${artist.added_by.user_name}">
            ${artist.added_by.user_name}</a></p>
        <p><h5>Similar Bands:</h5> ${artist_list(artists=artist.similars)}</p>
        <p><h5>Added:</h5> ${artist.fcreated}</p>
        <p><h5>Changed:</h5> ${artist.fupdated}</p>
        <p py:if="tracked_count"><h5>Users tracking:</h5> ${tracked_count}</p>
        </p>
        
        <p><h5>Upcoming events:</h5></p>
        <table class="upcoming" cellspacing="0">
             <tr py:for="e in future_events">
                 <td class="who" width="25%"><a href="/events/${e.id}">${e.name}</a></td>
                 <td class="when" width="25%"><a href="/events/${e.id}">${e.fdate} ${e.time}</a></td>
             </tr>             
        </table>
        <p py:if="not len(list(future_events))">None</p>
        <br clear="all"></br>

        <p><h5> Past events <span class="small">(<a href="?list_all=1">See all</a>)</span></h5></p>
        <table class="past" cellspacing="0">
            <tr py:for="e in past_events">
                <td class="who" width="25%"> <a href="/events/${e.id}">${e.name}</a></td>
                <td class="when" width="25%"> <a href="/events/${e.id}">${e.fdate}</a></td>
            </tr>             
        </table>
        <p py:if="not len(list(past_events))">None</p>

        <h5>Recordings</h5>
        <table>
            <tr py:for="r in artist.recordings">
                <td><img src="${r.img_url}" width="50" py:if="r.img_url" /></td>
                <td><a href="${r.url}">${r.name}</a></td>
            </tr>
        </table>
    </div>
</body>
</html>
