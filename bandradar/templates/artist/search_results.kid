<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <title>BandRadar - Band List</title>
</head>

<body>

  <div id="band">
  <h5>Artist Search Results</h5>
  <ul>
    <li py:for="a in artists">
      <a href="/artists/${a.id}">${a.name}</a>
     </li>
    </ul>
    </div>
</body>
</html>
