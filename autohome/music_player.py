import spotipy
import os

from random import sample
from spotipy.oauth2 import SpotifyPKCE
from dotenv import find_dotenv, load_dotenv


class MusicPlayer(spotipy.Spotify):
    """
    This module is responsible for reading a playlist named after the sentiment
    predicted by the autohome app.

    The user should have one of each of the following playlists on Spotify:
        - Happy
        - Sad
        - Neutral
        - Angry

    Each playlist must have at least 5 songs, chosen by the user and related to
    their label.

    Your local .env should have the following environmental variables:
        - SPOTIPY_CLIENT_ID
        - SPOTIPY_CLIENT_SECRET
        - SPOTIPY_REDIRECT_URI
    """

    def __init__(self) -> None:

        env_path = find_dotenv()
        load_dotenv(env_path)

        cwd = os.getcwd()
        print(cwd)
        cache_path = cwd + '/autohome/caches/cache'
        print(cache_path)


        if os.path.exists(cache_path):
            os.remove(cache_path)


        scope = [
            "playlist-read-private",
            "user-modify-playback-state",
            "user-read-playback-state",
            "user-read-currently-playing",
            "app-remote-control",
            "streaming",
            "playlist-modify-public",
            "playlist-modify-private"
        ]

        self.auth = SpotifyPKCE(scope=scope, cache_path=cache_path, open_browser=True)
        super().__init__(auth_manager=self.auth)
        self.user_id = self.current_user()["id"]
        self.playlist_uri = None
        self.playlist_id = None
        self.recommendations_uri = None
        self.device = None
        self.mood = None

    def get_playlist_uri(self) -> tuple:
        """
        This method reads the user's playlist names and, if it finds one
        correspondent to the predicted mood, returns its URI and URL.
        -----------
        Returns:
            - (playlist_uri: str, playlist_id: str)

        """
        playlists = self.current_user_playlists()["items"]

        for n in range(len(playlists)):
            if playlists[n]["name"].upper() == self.mood.upper():
                self.playlist_uri = playlists[n]["uri"]
                self.playlist_id = playlists[n]["id"]

        return self.playlist_uri, self.playlist_id


    def get_recomendations_uri(self, n_recoms=50) -> list:
        """
        This method takes a sample of 5 tracks from the mood's playlist and uses
        Spotify's recommendation algorithm to return a list of n_recoms tracks'
        URIs.
        ----------------------
        Parameters:
            - n_recoms: Number of recommended tracks to get. Must be an integer
                        from 1 to 99. Default value = 50.
        ----------------------
        Returns:
            - recommendations_uri: list
        """
        if not self.playlist_uri:
            self.playlist_uri, self.playlist_id = self.get_playlist_uri()

        tracks = self.playlist_tracks(self.playlist_uri)["items"]
        self.tracks_uri = [tracks[n]["track"]["uri"] for n in range(len(tracks))]

        self.seeds = sample(self.tracks_uri, 5)

        recommendations = self.recommendations(seed_tracks=self.seeds, limit=n_recoms)[
            "tracks"
        ]
        self.recommendations_uri = [
            recommendations[n]["uri"] for n in range(len(recommendations))
        ]

        return self.recommendations_uri


    def create_custom_playlist(self, mood) -> str:
        """
        This method takes the recommendated tracks and add to the current mood's
        playlist, by default, and returns the playlist's URI and URL.
        --------------
        Parameters:
            - new_playlist: False (default) -> adds the tracks to the mood's
                            playlist.
                            True -> creates a new playlist {mood}_new and adds
                            the recommended tracks.
        --------------
        Returns:
            - (playlist_uri: str,.playlist_id: str)
        """
        self.mood = mood

        if not self.recommendations_uri:
            self.recommendations_uri = self.get_recomendations_uri()

        self.user_playlist_remove_all_occurrences_of_tracks(
            self.user_id,
            self.playlist_id,
            self.tracks_uri
        )

        self.playlist_add_items(self.playlist_uri, self.tracks_uri[:5])
        self.playlist_add_items(self.playlist_uri, self.recommendations_uri)

        return self.playlist_uri


    def get_device_id(self) -> str:
        '''
        This method returns the current device's ID
        '''
        if not self.device:
            try:
                self.device = self.devices()['devices'][0]['id']
            except:
                return None

        return self.device


    def play_new_playlist(self) -> None:
        """
        This method toggles on the shuffle on the player and automatically
        starts to play the new playlist on the chosen device.
        """
        if not self.device:
            self.get_device_id()

        try:
            self.volume(35)
            self.start_playback(device_id=self.device, context_uri=self.playlist_uri)
            self.shuffle(True)
        except:
            return "No active device"

    def clear_instance(self):
        self.playlist_uri = None
        self.playlist_id = None
        self.recommendations_uri = None
        self.device = None
        self.mood = None


if __name__ == "__main__":
    sp = MusicPlayer()
    sp.create_custom_playlist('angry')
    id = sp.devices()
    print(id)
    sp.clear_instance()
    print(sp.mood)
    print(sp.playlist_uri)
