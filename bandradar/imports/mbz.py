# Importer for Musicbrainz service

from musicbrainz2 import webservice as ws
from musicbrainz2 import utils as mbutils
from musicbrainz2 import model as m
import urllib

def artist_info(artist_name):
    info = dict(members=None, wikipedia=None, homepage=None)
    # short names are bad
    if len(artist_name) < 3:
        return
    q = ws.Query()
    filt = ws.ArtistFilter(artist_name, limit=10)
    results = q.getArtists(filt)
    results = [x for x in results if x.score >= 99]
    # too many high scoring hits, can't disambiguate automatically
    if len(results) != 1:
        return info
    artist = results[0].artist
    uuid = mbutils.extractUuid(artist.id)
    inc = ws.ArtistIncludes(artistRelations=True, urlRelations=True)
    artist = q.getArtistById(uuid, inc)
    urls = artist.getRelationTargets(m.Relation.TO_URL, m.NS_REL_1+'Wikipedia')
    if len(urls):
        info['wikipedia'] = urllib.unquote(urls[0])
    urls = artist.getRelationTargets(m.Relation.TO_URL, m.NS_REL_1+'OfficialHomepage')
    if len(urls):
        info['homepage'] = urllib.unquote(urls[0])
    if artist.type == m.Artist.TYPE_GROUP:
        members = artist.getRelations(m.Relation.TO_ARTIST, m.NS_REL_1+'MemberOfBand')
        addl_uri = m.NS_REL_1+'Additional'
        coreMembers = [r for r in members if addl_uri not in r.attributes]
        info['members'] = ", ".join([x.target.name for x in coreMembers if not x.endDate])
        if info['members'] == "":
            info['members'] = None
    return info

if __name__ == "__main__":
    print artist_info(u"Santana")

