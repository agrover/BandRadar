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
  
  <div class="content">
   <div id="search">
    ${tg_global_search_form(action="/artists/search")}
    </div>
    
     <div class ="leftcontent">
        <div py:if="tg_flash" class="flash" py:content="tg_flash"></div>
        <div id="navcontainer">
        <ul id="navlist">
          <li id="login"><span py:if="not tg.identity.user">
              <img src="/static/images/key.png"/><a href="/users/login"> Log In</a>
          </span>
          <span py:if="tg.identity.user"><img src="/static/images/user.png"/>
              <a href="/users/${tg.identity.user.user_name}">
              ${tg.identity.user.user_name}'s Page</a>
          </span></li>
           
          
          <li><img src="/static/images/music.png"/><a href="/artists/list">  Bands</a></li>                
         <li><img src="/static/images/calendar.png"/><a href="/events/list">  Events</a></li> 
         <li><img src="/static/images/building.png"/><a href="/venues/list">  Venues</a></li>
         <li><img src="/static/images/lightbulb.png"/><a href="/faq">  faq</a></li>
         <li id="nav-logout"><span py:if="tg.identity.user"> <img src="/static/images/key_delete.png"/>
              <a href="/users/logout">  Logout</a>
          </span></li>
          <li><span py:if="'admin' in tg.identity.groups">
            <li><a href="/importers/webimport">Import Events</a></li>
            <li><a href="/importers/review">Review Events</a></li>
            <li><a href="/importers/reviewdupes">Possible dupes</a></li>
            <li><a href="/comments/list">Comments</a></li>
            <li><a href="/list_update_log">Updates</a></li>
            <li><a href="/list_batch">Batches</a></li>
          </span></li>
          
         
         </ul>
        </div>
     </div> 

     <div class="centercontent">
        <div id="banner">
    	  <a href="/"><img src="/static/images/banner.png" alt="BandRadar logo" /></a>
        </div>     
        <div py:replace="[item.text] + item[:]"/> 
       </div>

    <div class="rightcontent">  
        <div id="sitestats">
      	   <div id="bandstats">    
           <h5>Top Tracked Bands</h5>
           ${tg_top_artists()}
           </div>     
           <div id="venuestats">    
           <h5>Top Tracked Venues</h5>
           ${tg_top_venues()}
           </div>	
        </div>                   
   </div>  


  </div>

  <div class="footer">
    <a href="/faq">faq</a> |
    <a href="/about">about</a> |
    <a href="/privacy">privacy</a> |
    <a href="http://bandradar.blogspot.com">blog</a> |
    <a href="/contact">contact</a> |
    <a href="/comments/add">comments</a> |      
    <p>© Copyright 2007 <a href ="http://buunabet.com">Buunabet,LLC</a>  All rights reserved.</p>
  </div>
  
</body> 
</html>
