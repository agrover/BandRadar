function gmap_load() {
    if (GBrowserIsCompatible()) {
        map = new GMap2(document.getElementById("map"));
        map.addControl(new GSmallMapControl());
        point = new GLatLng(map_lat, map_lon)
        map.setCenter(point, 15);
        var marker = new GMarker(point);
        map.addOverlay(marker);
    }
}

addLoadEvent(gmap_load)

window.onunload = GUnload()
