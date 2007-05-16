<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <title>BandRadar - Band List</title>
</head>

<body>

   <div class="content">
      
    <div id="searchbox">
        <h2>Search Bands</h2>
        <?python from bandradar.artists import artist_search_form ?>
        ${artist_search_form(action="/artists/search")}
    </div>
<br clear="all"></br>
  <h5>Artist Search Results</h5>
    <p py:for="a in artists">
        <p><b><a href="/artists/${a.id}">${a.name}</a></b></p>
    </p>

    <p>
        ${tg_ButtonWidget(action="/artists/edit", label="Add a new Band")}
    </p>
    </div>
</body>
</html>
