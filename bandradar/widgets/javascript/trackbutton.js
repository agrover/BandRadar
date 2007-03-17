function button_pushed(action, id) {

    dom = $("item_" + id);

    function callback(xmlhttp) {
        text = xmlhttp.responseText;
        dom.innerHTML = text;
        if (!compare(text, "Tracked")) {
            addElementClass(dom, "tracked")
        }
        else {
            removeElementClass(dom, "tracked")
        }
    }
    
    function ajax_error(err) {
        if (err.number == 403)
            window.location = "/users/login"
        else
            alert("AJAX error: " + err.number);
    }        

    tracked = false
    if (!compare(scrapeText(dom).match(/(\S+)/)[1], "Tracked")) {
        tracked = true
    }
    d = doSimpleXMLHttpRequest(action, {id:id, tracked:tracked});
    d.addCallbacks(callback, ajax_error);
}

