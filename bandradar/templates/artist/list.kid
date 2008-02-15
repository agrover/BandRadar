<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <title>BandRadar - Band List</title>
</head>

<body>
<!--      <div id="help"><p>BandRadar sends you an email when your tracked bands add shows.</p>
     </div> -->
     <img src="/static/images/icon.png"/><a href="/artists/edit">ADD BAND or ARTIST</a>
     <p><h5>Bands playing ${listby}<big> (${count})</big></h5></p>     

        <ul id="listnavlist">
        <li><a href="/artists/list/today">Today</a></li>
        <li><a href="/artists/list/tomorrow">Tomorrow</a></li>
        <li><a href="/artists/list/yesterday">Yesterday</a></li>
        <li><a href="/artists/list/week">Week</a></li>
        <li><a href="/artists/list/all">All Upcoming</a></li>
        </ul>


                  
      <div id="band">
       
        <ul>       
        <li py:for="artist in artists">
        
            ${tg_track_button(tracked=artist['is_tracked'], id=artist['id'], action="/artists/dyntrack")}
            <b py:strip="not artist['is_tracked']">
                <a href="/artists/${artist['id']}">${artist['name']}</a></b>
                @ ${artist['venue_name']}
            
            </li>
           </ul>
  
    </div>
</body>
</html>
