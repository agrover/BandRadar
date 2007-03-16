from turbogears import config
from BeautifulSoup import BeautifulStoneSoup as bs
import urllib

localhost_key = "ABQIAAAAl6v2YpcT3a-0chb1euUaRRR4EqRj3RNZnoYuzojShxUjcPQKRRSqdkDEb-kjqUA2B3UAs66NGlvjOA" 
real_key = "ABQIAAAAl6v2YpcT3a-0chb1euUaRRRIOcczJVkwMVJxSoSbKoEvbYERDxTrKIpffL5C_3zzzlk1QmARAtbL2A"

if config.get("server.environment", "development") == "development":
    key = localhost_key
else:
    key = real_key

def get_geocode(address):
    base_req = "http://maps.google.com/maps/geo?"
    address_enc = address.replace(" ", "+")
    full_req = base_req + "key=%s&" % key + "output=xml&" + "q=%s" % address_enc
    usock = urllib.urlopen(full_req)
    soup = bs(usock.read())
    if soup.response.code.string != "200":
        raise IOError
    return soup.response.placemark.point.coordinates.string.split(",")[:2]
