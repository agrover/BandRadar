function gmap_load() {
    if (GBrowserIsCompatible()) {
        map = new GMap2(document.getElementById("map"));
        map.addControl(new GSmallMapControl());
        map.addControl(new GMapTypeControl());
        geocoder = new GClientGeocoder();

        function showAddress(address) {

            function gotGeocode(point) {
              if (!point) {
                alert(address + " not found");
              } else {
                map.setCenter(point, 15);
                var marker = new GMarker(point);
                map.addOverlay(marker);
                marker.openInfoWindowHtml("<b>"+scrapeText($('name'))+"</b><br/>"+address+"<br/>"+scrapeText($('phone')));
              }
            }

          geocoder.getLatLng(address+",Portland,OR",gotGeocode);
        }

        showAddress(scrapeText($('address')));
    }
}


addLoadEvent(gmap_load)

window.onunload = GUnload()
