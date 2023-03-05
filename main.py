from bs4 import BeautifulSoup
import requests as rq
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from api import USER_ID, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
from datetime import datetime

class TimeMachine:
    def __init__(self):
        scope = "playlist-modify-public playlist-modify-private"
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=CLIENT_ID, client_secret=CLIENT_SECRET, redirect_uri=REDIRECT_URI))

    def get_date(self):
        date_str = input("Enter a date in the format YYYY MM DD: ")
        self.date = datetime.strptime(date_str, "%Y %m %d").strftime("%Y-%m-%d")

    def billboard_scrape(self):
        print("Scraping the Billboard site...")
        response = rq.get(f"https://www.billboard.com/charts/hot-100/{self.date}/")
        soup = BeautifulSoup(response.text, "html.parser")

        # Combine #1 and #2-99 due to site formatting
        songs_1 = soup.find_all(name="h3", class_="c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 u-font-size-23@tablet lrv-u-font-size-16 u-line-height-125 u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-245 u-max-width-230@tablet-only u-letter-spacing-0028@tablet")
        songs_99 = soup.find_all(name="h3", class_="c-title a-no-trucate a-font-primary-bold-s u-letter-spacing-0021 lrv-u-font-size-18@tablet lrv-u-font-size-16 u-line-height-125 u-line-height-normal@mobile-max a-truncate-ellipsis u-max-width-330 u-max-width-230@tablet-only")
        songs = songs_1 + songs_99
        self.song_list = [song.get_text().strip() for song in songs]

        artists_1 = soup.find_all(name="span", class_="c-label a-no-trucate a-font-primary-s lrv-u-font-size-14@mobile-max u-line-height-normal@mobile-max u-letter-spacing-0021 lrv-u-display-block a-truncate-ellipsis-2line u-max-width-330 u-max-width-230@tablet-only u-font-size-20@tablet")
        artists_99 = soup.find_all(
            name="span",
            class_="c-label a-no-trucate a-font-primary-s lrv-u-font-size-14@mobile-max u-line-height-normal@mobile-max u-letter-spacing-0021 lrv-u-display-block a-truncate-ellipsis-2line u-max-width-330 u-max-width-230@tablet-only")
        artists = artists_1 + artists_99
        self.artist_list = [artist.get_text().strip() for artist in artists]

    def create_playlist(self):
        print("Creating playlist...")
        playlist = self.sp.user_playlist_create(user=USER_ID, name=f"{self.date} Top 100", public=True, collaborative=False, description=f"Billboard Top 100 on {self.date}, made with love using Python")
        self.playlist_id = playlist["id"]

    def add_songs(self):
        print("Adding songs to playlist...")
        song_ids = []

        # Find matches for each song
        for n in range(100):
            result = self.sp.search(
                q=f"artist: {self.artist_list[n]} track: {self.song_list[n]}", limit=1)
            song_id = result["tracks"]["items"][-1]["uri"]
            song_ids.append(song_id)

        self.sp.playlist_add_items(playlist_id=self.playlist_id, items=song_ids)
        print("Done")

timemachine = TimeMachine()
timemachine.get_date()
timemachine.billboard_scrape()
timemachine.create_playlist()
timemachine.add_songs()
