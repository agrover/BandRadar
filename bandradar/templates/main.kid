<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <title>BandRadar - Main</title>
</head>

<body>

  <div id="blurb">${XML(blurb)}</div>
  
  <div id="tonight">
    <ul class="tonight">
      <li py:for="event_id,event_name,venue_name in events">
  	  <a href="/events/${event_id}"><b>${venue_name}</b>:  ${event_name}</a></li>
    </ul>
  </div> 

</body>
</html>
