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
     <div py:if="tg_flash" class="flash" py:content="tg_flash"></div>
     <div py:replace="[item.text] + item[:]"/> 
   
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
