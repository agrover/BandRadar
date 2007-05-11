<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#"
    py:extends="'../master.kid'">

<head>
    <title>BandRadar - Band List</title>
</head>

<body>
     <div class="content">
     <div id="help">BandRadar sends you an email when your tracked bands add shows.</div>
     <div id="searchbox">
        <h3>Search all Bands</h3> 
        ${artist_search_form(action="/artists/search")}
        <?python from bandradar.artists import artist_search_form ?> 
     </div>
      
  
   <div class="content">
   <div id="bandstats"><h5> Bands playing ${listby} <big>(${count})</big></h5></div>
        <ul>
       <!--  <h3>With Shows</h3>&nbsp;&nbsp;  --> 
        <li><a href="/artists/list/today">Today</a></li>
        <li><a href="/artists/list/tomorrow">Tomorrow</a></li>
        <li><a href="/artists/list/yesterday">Yesterday</a></li>
        <li><a href="/artists/list/week">Upcoming week</a></li>
        <li><a href="/artists/list/all">All upcoming</a></li>
       <!--  <li> <div class="rightbutton">${tg_ButtonWidget(action="/artists/edit", label="Add a new Band")}</div></li> -->
       </ul>
            
      <div id="band">
      <table>
        <tr py:for="artist in artists">
            <td>
                <b py:strip="not artist['is_tracked']">
                <a href="/artists/${artist['id']}">${artist['name']}</a></b>
            </td>
            <td>${tg_track_button(tracked=artist['is_tracked'], id=artist['id'], action="/artists/dyntrack")}
            </td>
        </tr>
    </table>
    </div>
</div> 
</div>
</body>
</html>
