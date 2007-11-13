<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <title>BandRadar - Venue List</title>
</head>

  <body>
    <div id="help"><p>When you track a venue, BandRadar sends you a weekly email with upcoming events.</p><p><img src="/static/images/building_add.png"/> <a href="/venues/edit">Add a Venue</a></p></div>   

      <div id="venue">
        <ul>
            <li py:for="v in venues">
              ${tg_track_button(tracked=v['id'] in tracked_venues, id=v['id'], action="/venues/dyntrack")}
     
            <a href="/venues/${v['id']}">${v['name']}</a> <span py:if="v['eventcount']"> (${v['eventcount']} upcoming)</span>
              </li>
 
            
     </ul>
    </div>
  </body>
</html>
