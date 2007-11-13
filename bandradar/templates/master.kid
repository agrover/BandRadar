<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">

<?python import sitetemplate ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="sitetemplate">

<div class="edit_links" py:def="edit_links(object)">
    <?python from bandradar.util import can_edit, can_delete ?>
    <?python clsname = str.lower(object.__class__.__name__) ?>
    <p py:if="can_edit(object)">
        ${tg_ButtonWidget(action="/%ss/%d/edit" % (clsname, object.id), label="Edit this %s" % clsname)}
    </p>
    <p py:if="can_delete(object)">
        ${tg_ButtonWidget(action="/%ss/%d/delete" % (clsname, object.id), label="Delete this %s" % clsname)}
    </p>
</div>

 <!-- <div py:def="nav()"> -->
 
           
  <div class="admin_nav" py:if="'admin' in tg.identity.groups">
        <a href="/importers/webimport">Import Events</a>
        <a href="/importers/review">Review Events</a>
        <a href="/importers/reviewdupes">Possible dupes</a>
                <a href="/comments/list">Comments</a>
        <a href="/list_update_log">Updates</a>
        <a href="/list_batch">Batches</a>
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
          <!-- <img src="/static/images/top_bk.png"/> -->
<!--     ${tg_global_search_form(action="/artists/search")}  -->


    <!--   <div py:replace="nav()" /> -->
    
  <div class="content">
    
    <div class ="leftcontent">
      <div id="navcontainer">
        <ul id="navlist">
          <li id="login"><span py:if="not tg.identity.user">
              <img src="/static/images/key.png"/><a href="/users/login"> Come In!</a>
          </span>
          <span py:if="tg.identity.user"><img src="/static/images/user.png"/>
              <a href="/users/${tg.identity.user.user_name}">
              ${tg.identity.user.user_name}'s Page</a>
          </span></li>
          
          <li><img src="/static/images/music.png"/><a href="/artists/list">  Bands</a></li>                
          <!-- <li id="nav-bands"><a href="/artists/list">Bands</a></li> -->
          <li><img src="/static/images/calendar.png"/><a href="/events/list">  Events</a></li> 
          <!-- <li id="nav-events"><a href="/events/list">Events</a></li> -->
          <li><img src="/static/images/building.png"/><a href="/venues/list">  Venues</a></li>
          <!-- <li id="nav-venues"><a href="/venues/list">Venues</a></li> -->
          <li id="nav-logout"><span py:if="tg.identity.user"> <img src="/static/images/key_delete.png"/>
              <a href="/users/logout">  Logout</a>
          </span></li>
        </ul>
      </div>
      <div py:if="tg_flash" class="flash" py:content="tg_flash"></div>
       <!-- <div id="tagline">
          <p>Track your favorite artists and venues! Get notified when new events
              come to town.blahahahahahahahah.</p>  
        </div> -->
    </div> 

    <div class="centercontent">
    
      <div id="banner">
  	  <a href="/"><img src="/static/images/banner.png" alt="BandRadar logo" /></a>
      </div>
  
     <!-- <div py:if="tg_flash" class="flash" py:content="tg_flash"></div> -->
     <div py:replace="[item.text] + item[:]"/> 
    </div>

    <div class="rightcontent">
    <div id="search">
    ${tg_global_search_form(action="/artists/search")}
    </div>
      <!-- ${tg_global_search_form(action="/artists/search")} -->
     
   <!-- <div id="sitestats">
  	  <div id="bandstats">    
          <h5>Top Tracked Bands</h5>
          <p py:for="item in top_artists">
          <a href="/artists/${item['id']}">${item['name']}</a></p>
          </div>        
          <div id="eventstats">
          <h5>Top Tracked Events</h5>
          <p py:for="item in top_events">
          <a href="/events/${item['id']}">${item['name']}</a></p>
          </div>     
          <div id="venuestats">    
          <h5>Top Tracked Venues</h5>
          <p py:for="item in top_venues">
          <a href="/venues/${item['id']}">${item['name']}</a></p>
        </div>	
      </div>   -->
                 
    </div>  


  </div>

  <div class="footer">
    <a href="/faq">faq</a> |
    <a href="/about">about</a> |
    <a href="/privacy">privacy</a> |
    <a href="http://bandradar.blogspot.com">blog</a> |
    <a href="/contact">contact</a> |
    <a href="/comments/add">comments</a> |      
    <a href="/feeds">rss</a>

    <p>© Copyright 2007 Buunabet,LLC All rights reserved.</p>
  </div>
  
</body> 
</html>
