import os

import requests
import spotipy
from bs4 import BeautifulSoup
from spotipy.oauth2 import SpotifyOAuth

YEAR = 2021
LINEUP_URL = "https://www.damnationfestival.co.uk/lineup"

# ------------- SET UP -----------
CLIENT_ID = os.environ.get("CLIENT_ID")  # CHANGE THESE TO YOUR OWN
CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
playlist_id = "5rwVvahN41qAu6Ws1wJfhe"  # UNCOMMENT WHEN YOU HAVE STORED YOUR PLAYLIST VARIABLE

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private playlist-modify-public",
        redirect_uri="http://example.com",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        show_dialog=True,
        cache_path="token.txt"
    )
)
user_id = sp.current_user()["id"]

# # -------- Create Playlist ----------
# # COMMENT THIS SECTION OUT IF YOU ALREADY HAVE A PLAYLIST

# playlist_name = f"Damnation {YEAR} playlist"
# playlist_description = f"Created with Python"
#
#
#
# playlist = sp.user_playlist_create(user_id,
#                                    playlist_name,
#                                    public=True,
#                                    description=playlist_description)
# playlist_id = playlist["id"]
# print(playlist_id)

# IMPORTANT: store playlist ID as 'playlist_id' for future use


# --------------- Scrape website -----------------

response = requests.get(LINEUP_URL)
lineup_site = response.text
soup = BeautifulSoup(lineup_site, "html.parser")

scraped_links = soup.find_all(name='a', class_="image-slide-anchor content-fill", href=True)

scraped_urls = [band['href'] for band in scraped_links]
band_urls = []
for band in scraped_urls:
    band_urls.append(band.split("?")[0])

new_bands = []
with open("lineup.txt", "a+") as fp:
    fp.seek(0)
    lineup_file = fp.readlines()
    current_list = [band.replace("\n", " ").strip() for band in lineup_file]

    for band in scraped_urls:
        if band not in current_list:
            new_bands.append(band)
            fp.write(band + "\n")

# Fix for Bell Witch
new_albums = []
for band in new_bands:
    if "album" in band:
        new_bands.remove(band)
        new_albums.append(band)

# # ---------- Get Top Tracks ------------

tracks = []

for uri in new_bands:
    results = sp.artist_top_tracks(uri)
    for track in results['tracks'][:10]:
        tracks.append(track['uri'])

for album in new_albums:
    results = sp.album_tracks(album)
    for track in results['items'][:]:
        tracks.append(track['uri'])

# # --------- Add tracks to playlist
#
# Hacky fix to get around 100 track max
len_tracks = len(tracks)
max_tracks = 100
counts = list(range(0, len_tracks, 100))
counts.append(len_tracks + 1)

if len_tracks > 100:
    for i in range(len(counts) - 1):
        add_tracks = tracks[counts[i]:counts[i + 1]]
        result = sp.playlist_add_items(playlist_id=playlist_id, items=add_tracks)
elif len_tracks == 0:
    print("Error: no new tracks")
else:
    result = sp.playlist_add_items(playlist_id=playlist_id, items=tracks)

print("Playlist compiled!")
