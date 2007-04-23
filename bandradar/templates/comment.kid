<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'master.kid'">

<head>
    <title>BandRadar - Comment</title>
</head>

<body>

<div class="content">
    <h2>So What Do You Think?</h2>
    <p>Any <b>BandRadar</b> features you'd like to see, bugs you found, or other sorts of feedback.</p>
    <p> If you're logged in we can even get back to you!</p>

    ${comment_form(action="/comments/save")}
</div>

</body>
</html>
