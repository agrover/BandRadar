<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <title>BandRadar - Comment</title>
</head>

<body>
    <h3>Please give us any comments you have on features you'd like to see, bugs
    you found, or anything else you think of. If you're logged in, we can even
    get back to you! Thanks -- BR Staff</h3>

    ${comment_form(action="/commentsave")}

</body>
</html>
