import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv
from random import choice


load_dotenv()
#flow: user enters song title, get parsed into URL + title, we take title 
#TODO move data to DB like redis

class SpotifyController:
    def __init__(self, track_count=9):
        CLIENT_ID, CLIENT_SECRET = os.getenv("CLIENT_ID"), os.getenv("CLIENT_SECRET")

        #Spotipy query parameters
        auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
        self.sp = spotipy.Spotify(auth_manager=auth_manager)
        self.track_count = track_count

        self.playlist = []
        self.songs = set()
        self.artists = set()

    def insert_search_params(self, song: str) -> None:
        """
        Manages the sets that contain the search parameters for the Spotify API. Queries and converts 'song' into 'song link' + 'artist link' on spotify
        """

        if len(self.songs) > 3 and len(self.artists) > 3:
            return
        
        sp_res = self.sp.search(q=f"track:{song}", type=["track"], limit=1)

        try:
            artist_link = sp_res['tracks']['items'][0]['album']['artists'][0]['external_urls']['spotify']
            song_link = sp_res['tracks']['items'][0]['external_urls']['spotify']
        except Exception:
            print("didnt work")
            return
        
        print(song_link, artist_link)
        #update songs set, we check if len < 5 because "recommendations" endpoint has a limit of up to 5 parameters
        if len(self.songs) < 4:
            if song_link not in self.songs:
                self.songs.add(song_link)
        #update artist set
        if len(self.artists) < 4:
            if artist_link not in self.artists:
                self.artists.add(artist_link)


    def generate_recommended(self) -> None:               
        #TODO maybe use redis to store user's request logs and their artists to get artist/track seeds
        #add check if user's  genre are available using 'if genre in b'
        artist, song = [], []
        if len(self.artists) != 0:
            artist = [choice(list(self.artists))]
        if len(self.songs) != 0:
            song = [choice(list(self.songs))]
        
        #this api has a max 5 seed total constraint
        rec = self.sp.recommendations(seed_artists=artist, seed_tracks=song, seed_genres=["r-n-b", "pop", "hip-hop"], limit=self.track_count)
        
        tracks = rec['tracks']
        
        #TODO better way: 1. get all tracks. 2. execute search_yt() one at a time using !next method which we already have.
        self.playlist = []
        for i in range(len(tracks)):
            search_query = f"{tracks[i]['name']} by {tracks[i]['artists'][0]['name']}"
            self.playlist.append(search_query)
        
        print(self.playlist)
    
    def get_recommended(self) -> list[str]:
        return self.playlist

