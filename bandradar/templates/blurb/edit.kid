<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <title>BandRadar - Add or Edit a Blurb</title>
</head>
<body>
    Blurbs are formatted using <a href="http://docutils.sourceforge.net/docs/user/rst/quickref.html">
    reStructuredText formatting</a>.<br/>
    ${XML(form_vals.get('show_text', ''))}

    <h2 py:if="'id' in form_vals">Edit a blurb</h2>
    <h2 py:if="'id' not in form_vals">Add a blurb</h2>

    ${blurb_form(value=form_vals, action="/blurbs/save")}

</body>
</html>
