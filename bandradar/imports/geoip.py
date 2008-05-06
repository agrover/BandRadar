import import_util

base_url = "http://api.hostip.info/?ip="

def info(ip):
    soup = import_util.url_to_soup(base_url + ip)
    lon, lat = soup.hostiplookupresultset.find("gml:coordinates").string.split(",")
    city = soup.find("gml:featuremember").find("gml:name").string
    return dict(lat=lat, lon=lon, city=city)


if __name__ == "__main__":
    results = info("131.252.120.50")
    print results
