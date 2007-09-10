from imports import google
from decimal import Decimal

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
    hi_lat, lo_lat, hi_lon, lo_lon = radius_to_ll_bounds(ctr_lat, ctr_lon, radius)
    if not hi_lat >= lat >= lo_lat:
        return False
    if not hi_lon >= lon >= lo_lon:
        return False
    return True

def distance (a_lat, a_lon, b_lat, b_lon):
    """return distance between two coords in miles"""
    lat_delta = abs(a_lat-b_lat)
    lon_delta = abs(a_lon-b_lon)
    y_miles = lat_delta * Decimal("69.1691") 
    x_miles = lon_delta * Decimal("48.9097") # pdx only
    # good 'ol pythagorean theorem
    tmp = (y_miles*y_miles) + (x_miles*x_miles)
    return tmp.sqrt().quantize(Decimal("0.01"))

def get_geocode(location):
    return google.get_geocode(location)
