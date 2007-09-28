from BeautifulSoup import BeautifulStoneSoup as bs
from datetime import date
import urllib
import re

baseurl = "http://ecs.amazonaws.com/onca/xml"
access_key = "0S381N0APYWVHYRS8BR2"
affiliate_tag = "band08-20"

def recordings(name, count=5):
    """Return names of albums by a given artist on Amazon.

    Amazon only returns 10 results, so setting count higher will
    have no effect."""
    req = {}
    req['SearchIndex'] = "Music"
    req['Service'] = "AWSECommerceService"
    req['AWSAccessKeyId'] = access_key
    req['AssociateTag'] = affiliate_tag
    req['Operation'] = "ItemSearch"
    req['Version'] = "2007-07-16"
    req['ResponseGroup'] = "Images,Small"
    req['Sort'] = 'salesrank'
    req['Artist'] = urllib.quote(name.encode('utf8'))
    params = "&".join([key+"="+value for key, value in req.items()])
    url = baseurl + "?" + params
    usock = urllib.urlopen(url)
    soup = bs(usock.read())
    if soup.itemsearchresponse.items.request.isvalid.string != "True":
        return
    # do something if it took too long?
    time = float(soup.itemsearchresponse.operationrequest.requestprocessingtime.string)
    items = soup.itemsearchresponse.items.findAll('item')
    for item in items[:count]:
        if item.artist.string != name:
            continue
        a = {}
        a['name'] = item.title.string
        a['url'] = item.detailpageurl.string
        try:
            a['img_url'] = item.smallimage.url.string
        except AttributeError:
            a['img_url'] = None
        yield a

if __name__ == "__main__":
    print list(recordings("Metallica", count=1))

