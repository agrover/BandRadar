<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <title>BandRadar - Import From Web</title>
</head>

<body>
    <h3>Import WWeek?</h3>

    ${wweek_form(action="/importers/importwweek")}

    <h3>Import Pollstar?</h3>

    <form action="/importers/importpollstar" method="post" class="tableform" name="pollstar">        
        <input type="submit" class="submitbutton" value="Go" />
    </form>

    <h3>Import Upcoming.org?</h3>

    <form action="/importers/importupcoming" method="post" class="tableform" name="upcoming">        
        <input type="submit" class="submitbutton" value="Go" />
    </form>

</body>
</html>
