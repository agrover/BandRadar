<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <title>BandRadar - Closest events to ${start}</title>
</head>

<body>

<?python import urllib ?>

  <div id="events">
    <ul>
      <li py:for="venue, distance in venues">
        <p py:for="event in venue.today_events">
  	      <a href="/venues/${venue.id}"><b>${venue.name}</b> (${venue.address})</a>:
          <a href="/events/${event.id}">${event.name} (${distance} miles)</a>
          <a href="http://maps.google.com/maps?daddr=${venue.geocode_lat},${venue.geocode_lon}&amp;saddr=${saddr}">Directions</a>
        </p>
      </li>
    </ul>
  </div> 

</body>
</html>
