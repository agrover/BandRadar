<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <title>BandRadar - Add or Edit a Band</title>
</head>
<body>


    <h2 py:if="'id' in form_vals">Edit a band</h2>
    <h2 py:if="'id' not in form_vals">Add a band</h2>

    ${artist_form(value=form_vals, action="/artists/save")}
    


</body>
</html>
