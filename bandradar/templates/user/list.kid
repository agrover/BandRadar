<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <title>BandRadar - User List</title>
</head>

<body>
    <h2>User List</h2>

    <p py:for="u in users">
        <p><a href="/users/${u.user_name}">${u.user_name}</a> tracking ${u.artists.count()}, added ${u.get_fcreated()}</p>
    </p>
</body>
</html>
