function button_pushed(action, id, text_off, text_on) {

    dom = $("item_" + id);

    function callback(xmlhttp) {
        text = xmlhttp.responseText;
        if (!compare(text, "Tracked")) {
            addElementClass(dom, "tracked")
            dom.innerHTML = text_on
        }
        else {
            removeElementClass(dom, "tracked")
            dom.innerHTML = text_off
        }
    }
    
    function ajax_error(err) {
        if (err.number == 403)
            window.location = "/users/login"
        else
            alert("AJAX error: " + err.number);
    }        

    track = false
    if (!compare(scrapeText(dom).match(/(\S+)/)[1], text_off)) {
        track = true
    }
    d = doSimpleXMLHttpRequest(action, {id:id, track:track});
    d.addCallbacks(callback, ajax_error);
}

