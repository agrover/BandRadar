import imports.scrobxlib

def user_top_artists(user_name, limit=10):
    return [artist['name'] for artist in scrobxlib.topArtists(user_name)[:limit]]

def similar_artists(artist_name, limit=3):
    artist_name = artist_name.replace(" ", "+")
    try:
        similar_artists = scrobxlib.similar(artist_name)[:limit]
    except:
        return list()
    return [artist['name'] for artist in similar_artists]


if __name__ == "__main__":
    print user_top_artists("agrover", 4)
