import urllib
from decimal import Decimal
from bandradar import util
import import_util

localhost_key = "ABQIAAAAl6v2YpcT3a-0chb1euUaRRR4EqRj3RNZnoYuzojShxUjcPQKRRSqdkDEb-kjqUA2B3UAs66NGlvjOA" 
real_key = "ABQIAAAAl6v2YpcT3a-0chb1euUaRRRIOcczJVkwMVJxSoSbKoEvbYERDxTrKIpffL5C_3zzzlk1QmARAtbL2A"

if util.is_production():
    key = real_key
else:
    key = localhost_key

def get_geocode(address):
    base_req = "http://maps.google.com/maps/geo?"
    address_enc = urllib.quote_plus(address)
    full_req = base_req + "key=%s&" % key + "output=xml&" + "q=%s" % address_enc
    soup = import_util.url_to_soup(full_req)
    if soup.response.code.string != "200":
        raise IOError
    # return reversed for [lat, lon] instead if [x, y] (which is lon, lat)
    l = list(reversed(soup.response.placemark.point.coordinates.string.split(",")[:2]))
    l = [Decimal(c) for c in l]
    try:
        zip_code = soup.response.placemark.addressdetails.country.administrativearea.subadministrativearea.locality.postalcode.postalcodenumber.string
    except AttributeError:
        zip_code = None
    l.append(zip_code)
    return l

