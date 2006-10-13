<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python import sitetemplate ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="sitetemplate">

<div py:def="venue_detail(venue)">
    <p><a href="/venues/${venue.id}">${venue.Name}</a></p>
    <p py:if="venue.Address">Address: ${venue.Address}</p>
    <p py:if="venue.Url">Website: <a href="${venue.Url}">xx</a></p>
    <p py:if="venue.Phone">Phone: ${venue.Phone}</p>
</div>

<div py:def="edit_links(id, type)">
    <?python from turbogears import identity ?>
    <div py:if="'admin' in identity.current.groups">
        <p><a href="/${type}s/${id}/edit">Edit this ${type}</a></p>
        <p><a href="/${type}s/delete?id=${id}">Delete this ${type}</a></p>
    </div>
</div>

<head py:match="item.tag=='{http://www.w3.org/1999/xhtml}head'">
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" />
    <link rel="stylesheet" type="text/css" href="/static/css/main.css" />
    <script src="http://www.google-analytics.com/urchin.js" type="text/javascript">
    </script>
    <script type="text/javascript">
    _uacct = "UA-131305-2";
    urchinTracker();
    </script>
    <meta py:replace="item[:]"/>
</head>

<body py:match="item.tag=='{http://www.w3.org/1999/xhtml}body'">
    <?python from turbogears import identity ?>

    <div id="main_column">

        <div id="logo">
            <a href="/"><img src="/static/images/logo3md.png"/></a>
        </div>

        <div id="header">
            <span py:if="not identity.current.user">
                <a href="/users/login">Login/Register</a>
            </span>
            <span py:if="identity.current.user">
                <a href="/users/${identity.current.user.user_name}">${identity.current.user.user_name}'s Bands</a>
            </span>
            <a href="/artists/list">Bands</a>
            <a href="/events/list">Events</a>
            <a href="/venues/list">Venues</a>
            <span py:if="'admin' in identity.current.groups">
                <a href="/importers/webimport">Import Events</a>
                <a href="/importers/review">Review Events</a>
            </span>
            <span py:if="identity.current.user">
                <a href="/users/logout">Logout</a>
            </span>
        </div>

        <div py:if="tg_flash" class="flash" py:content="tg_flash"></div>

        <div id="content">
            <div py:replace="[item.text] + item[:]"/>
        </div>

        <div id="footer">
            <a href="/about">about</a> |
            <a href="/privacy">privacy</a> |
            <a href="/contact">contact</a> |
            <a href="/feeds">rss</a>
        </div>
    </div>
</body>
</html>
