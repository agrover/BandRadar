<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <title>BandRadar - Lost Password</title>
</head>

<body>
    <div class="content">
   <p> Please enter the email address you used to register, and an email will
    be sent to that address with your password.
    ${lost_passwd_form(action="/users/lost_passwd_send")}</p>
    </div>
</body>
</html>
