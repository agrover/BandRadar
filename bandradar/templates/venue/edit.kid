<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <title>BandRadar - Edit a Venue</title>
</head>

<body>
    <h2>Edit a venue</h2>

    <form action="/venues/save" method="post">
        <input type="hidden" name="id" value="${id}" />
        <label>Name:</label><input type="text" name="name" size="40" value="${name}"/><br/>
        <label>Address:</label><input type="text" name="addr" size="40" value="${addr}"/><br/>
        <label>URL:</label><input type="text" name="url" size="40" value="${url}"/><br/>
        <input type="submit" name="submit" value="Save!" />
    </form>
</body>
</html>
