<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <title>BandRadar - Import From Web</title>
</head>

<body>
    <h3>Import Mercury from web?</h3>

    ${merc_form(action="/importers/importmercury")}

    <h3>Import WWeek from web?</h3>

    ${wweek_form(action="/importers/importwweek")}

</body>
</html>
