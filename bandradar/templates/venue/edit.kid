<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <title>BandRadar - Edit a Venue</title>
</head>

<body>

    <h2>Edit a venue</h2>

    ${venue_form.display(value=form_vals, action="/venues/save")}


</body>
</html>
