<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <title>BandRadar - Edit a user</title>
</head>

<body>
    <h2>Edit ${user_name}</h2>

    ${user_form(value=form_vals, action="/users/save")}

</body>
</html>
