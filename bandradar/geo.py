from imports import google, geoip
from decimal import Decimal
try:
    from gps import EarthDistance, METERS_TO_MILES
except ImportError:
    pass # keep going, no one's using gps stuff yet

#from Google Answers
#Distance between one degree of longitude at a given latitude:
#(pi/180)*R*cosA where R is the radius of the earth in miles and A in
#the degree latitude.  The radius of the earth is 3963.1676 miles by
#the way.  I'll let you do the multiplication.  This is right, trust
#me.  I get paid lots of money to do much more complicated math.

def radius_to_ll_bounds(lat, lon, radius):
    """a cheezy way to implement "get x within y miles". lat/lon in db are most
    easily searched as a square (not circle). This function takes a point and
    generates upper/lower lat/lon based on distance in miles."""
    lat = Decimal(lat)
    lon = Decimal(lon)
    x_delta = Decimal(str(radius)) / Decimal("48.9097") # pdx only
    y_delta = Decimal(str(radius)) / Decimal("69.1691")

    l = (lat+y_delta, lat-y_delta, lon+x_delta, lon-x_delta)
    return l

def is_within_radius(ctr_lat, ctr_lon, radius, lat, lon):
    """is a point withing a given radius in miles from another point"""
    return distance(ctr_lat, ctr_lon, lat, lon) <= radius

def distance(a_lat, a_lon, b_lat, b_lon):
    """return distance between two coords in miles"""
    a_lat = float(a_lat)
    a_lon = float(a_lon)
    b_lat = float(b_lat)
    b_lon = float(b_lon)
    meters = EarthDistance((a_lat, a_lon), (b_lat, b_lon))
    miles = meters * METERS_TO_MILES
    return Decimal(str(miles)).quantize(Decimal("0.01"))

def get_geocode(location):
    return google.get_geocode(location)

def ip_to_lat_lon(ip):
    results = geoip.info(ip)
    lat = Decimal(results['lat'])
    lon = Decimal(results['lon'])
    return (lat, lon)
