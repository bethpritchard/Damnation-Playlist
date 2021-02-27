import os

import requests
import spotipy
from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyOAuth
from pprint import pprint

YEAR = 2021
LINEUP_URL = "https://www.damnationfestival.co.uk/lineup"

# ------------- SET UP -----------
client_id = os.environ.get("CLIENT_ID")
client_secret = os.environ.get("CLIENT_SECRET")

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private playlist-modify-public",
        redirect_uri="http://example.com",
        client_id=client_id,
        client_secret=client_secret,
        show_dialog=True,
        cache_path="token.txt"
    )
)
user_id = sp.current_user()["id"]

# IF PLAYLIST NOT CREATED, UNCOMMENT
# # -------- Create Playlist ----------
# # Comment this section if needed
# playlist_name = f"Damnation {YEAR} playlist"
# playlist_description = f"Created with Python"
# playlist = sp.user_playlist_create(user_id,
#                                    playlist_name,
#                                    public=True,
#                                    description=playlist_description)
# playlist_id = playlist["id"]
# print(playlist_id)

# # IMPORTANT: store playlist ID as 'playlist_id' for future use
playlist_id = os.environ.get("PLAYLIST_ID")

# --------------- Scrape website -----------------

response = requests.get(LINEUP_URL)
lineup_site = response.text
soup = BeautifulSoup(lineup_site, "html.parser")

bands_html = soup.find_all(name='div', class_="image-slide-title")
bands = [band.text for band in bands_html]
bands.append("Electric Wizard")


# Hacky fix for Bell Witch & Aerial Ruin
for band in bands:
    if "&" in band:
        bands.remove(band)
        split_band = band.split("&")
        for new_band in split_band:
            bands.append(new_band.strip())

# ------------- Store current lineup ------------
# Compares list of scraped bands to the current list

new_bands = []
with open("lineup.txt", "a+") as fp:
    fp.seek(0)
    lineup_file = fp.readlines()
    current_lineup = [band.replace("\n", " ").strip() for band in lineup_file]

    for band in sorted(bands):
        if band not in current_lineup:
            new_bands.append(band)
            fp.write(band + "\n")

# --------- Get Band Uris --------------
#
band_uris = []
for band in new_bands:
    result = sp.search(f"artist: {band}", type="artist")

    try:
        uri = result['artists']['items'][0]['uri']
        band_uris.append(uri)
    except IndexError:
        print(f"Error: {band} does not exist on Spotify")

# ---------- Get Top Tracks ------------

tracks = []

for uri in band_uris:
    results = sp.artist_top_tracks(uri)
    for track in results['tracks'][:10]:
        tracks.append(track['uri'])

# --------- Add tracks to playlist

# Hacky fix to get around 100 track max
len_tracks = len(tracks)
max_tracks = 100
counts = list(range(0,len_tracks,100))
counts.append(len_tracks+1)

if len_tracks > 100:
    for i in range(len(counts)-1):
        add_tracks = tracks[counts[i]:counts[i+1]]
        result = sp.playlist_add_items(playlist_id=playlist_id, items=add_tracks)
        print("Playlist compiled!")
elif len_tracks == 0:
    print("Error: no new tracks")
else:
    result = sp.playlist_add_items(playlist_id=playlist_id, items=tracks)
    print("Playlist compiled!")





