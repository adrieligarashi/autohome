import spotipy

from random import sample
from spotipy.oauth2 import SpotifyOAuth
from dotenv import find_dotenv, load_dotenv


class MusicPlayer(spotipy.Spotify):
    '''
    This module is responsible for reading a playlist named after the sentiment
    predicted by the autohome app.

    The user should have one of each of the following playlists on Spotify:
        - Happy
        - Sad
        - Neutral
        - Angry

    Each playlist must have at least 5 songs, chosen by the user and related to
    their label.
    '''
    def __init__(self, mood) -> None:

        env_path = find_dotenv()
        load_dotenv(env_path)

        scope = [
                'playlist-read-private', 'user-modify-playback-state',
                'user-read-playback-state', 'app-remote-control', 'streaming',
                'playlist-modify-public', 'playlist-modify-private'
            ]

        auth = SpotifyOAuth(scope=scope)
        super().__init__(auth_manager=auth)
        self.user_id = self.current_user()['id']
        self.playlist_uri = None
        self.recommendations_uri = None
        self.device = self.devices()['devices'][0]['id']
        self.mood = mood


    def get_playlist_uri(self) -> str:
        '''
        This method reads the user's playlist names and, if it finds one
        correspondent to the predicted mood, returns its URI.
        -----------
        Returns:
            - playlist_uri: str
        '''
        playlists = self.current_user_playlists()['items']

        for n in range(len(playlists)):
            if playlists[n]['name'].upper() == self.mood.upper():
                self.playlist_uri = playlists[n]['uri']

        return self.playlist_uri


    def get_recomendations_uri(self, n_recoms=50) -> list:
        '''
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
        '''
        if not self.playlist_uri:
            self.playlist_uri = self.get_playlist_uri()

        tracks = self.playlist_tracks(self.playlist_uri)['items']
        self.tracks_uri = [
            tracks[n]['track']['uri'] for n in range(len(tracks))
        ]

        self.seeds = sample(self.tracks_uri, 5)

        recommendations = self.recommendations(seed_tracks=self.seeds,
                                               limit=n_recoms)['tracks']
        self.recommendations_uri = [
            recommendations[n]['uri'] for n in range(len(recommendations))
        ]

        return self.recommendations_uri


    def create_custom_playlist(self, new_playlist=False) -> str:
        '''
        This method takes the recommendated tracks and add to the current mood's
        playlist, by default, and returns the playlist's URI.
        --------------
        Parameters:
            - new_playlist: False (default) -> adds the tracks to the mood's
                            playlist.
                            True -> creates a new playlist {mood}_new and adds
                            the recommended tracks.
        --------------
        Returns:
            - playlist_uri: string
        '''
        if not self.recommendations_uri:
            self.recommendations_uri = self.get_recomendations_uri()

        if not new_playlist:
            self.playlist_add_items(self.playlist_uri, self.recommendations_uri)
        else:
            self.user_playlist_create(self.user_id, f'{self.mood}_new'.capitalize())

            playlists = self.current_user_playlists()['items']

            for n in range(len(playlists)):
                if playlists[n]['name'].upper() == f'{self.mood}_new'.upper():
                    self.playlist_uri = playlists[n]['uri']

            self.playlist_add_items(self.playlist_uri,
                                    self.recommendations_uri)

        return self.playlist_uri


    def play_new_playlist(self) -> None:
        '''
        This method toggles on the shuffle on the player and automatically
        starts to play the new playlist on the chosen device.
        '''
        self.shuffle(True)
        self.start_playback(device_id=self.device, context_uri=self.playlist_uri)


if __name__ == '__main__':
    sp = MusicPlayer('Happy')
    sp.create_custom_playlist()
    sp.play_new_playlist()
    print('GREAT SUCCESS!')
