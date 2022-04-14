import spotipy

from random import sample
from spotipy.oauth2 import SpotifyOAuth
from dotenv import find_dotenv, load_dotenv

<<<<<<< HEAD
def get_env_vars():

    env_path = find_dotenv()
    load_dotenv(env_path)


def authorize_spotify(scope=[
    'playlist-read-private',
    'user-modify-playback-state',
    'user-read-playback-state',
    'app-remote-control',
    'streaming',
    'playlist-modify-public',
    'playlist-modify-private']) -> spotipy.Spotify:

    auth = SpotifyOAuth(scope=scope)
    sp = spotipy.Spotify(auth_manager=auth)

    return sp


def get_playlist_uri(sp, mood_template='Teste') -> str:

    playlist_uri = None
    playlists = sp.current_user_playlists()['items']

    for n in range(len(playlists)):
        if playlists[n]['name'] == mood_template:
            playlist_uri = playlists[n]['uri']

    return playlist_uri


def get_recommendations_uri(sp, playlist_uri, random_sample=True, n_recoms=50):

    tracks = sp.playlist_tracks(playlist_uri)['items']
    tracks_uri = [tracks[n]['track']['uri'] for n in range(len(tracks))]

    if random_sample:
        seeds = sample(tracks_uri, 5)
    else:
        seeds = tracks_uri[:5]

    recommendations = sp.recommendations(seed_tracks=seeds,
                                         limit=n_recoms)['tracks']

    recommendations_uri = [recommendations[n]['uri'] for n in range(len(recommendations))]

    return recommendations_uri


def create_custom_playlist(sp, recommendations_uri, mood='HACKERMAN!',
                           public=True, collaborative=False):

    user_id = sp.current_user()['id']

    playlist_uri = sp.user_playlist_create(user_id, mood, public=public,
                                           collaborative=collaborative)['uri']

    sp.playlist_add_items(playlist_uri, recommendations_uri)
=======

env_path = find_dotenv()
load_dotenv(env_path)

scope = [
    'playlist-read-private', 'user-modify-playback-state',
    'user-read-playback-state', 'app-remote-control', 'streaming',
    'playlist-modify-public', 'playlist-modify-private'
]

auth = SpotifyOAuth(scope=scope)


class MusicPlayer(spotipy.Spotify):

    def __init__(self) -> None:

        auth = SpotifyOAuth(scope=scope)
        super().__init__(auth_manager=auth)
        self.user_id = self.current_user()['id']
        self.template_playlist_uri = None
        self.recommendations_uri = None
        self.playlist_uri = None


    def get_playlist_uri(self, mood_template='Teste') -> str:

        playlists = self.current_user_playlists()['items']

        for n in range(len(playlists)):
            if playlists[n]['name'] == mood_template:
                self.template_playlist_uri = playlists[n]['uri']

        return self.template_playlist_uri


    def get_recomendations_uri(self, random_sample=True, n_recoms=50):

        if not self.playlist_uri:
            self.playlist_uri = self.get_playlist_uri()

        tracks = self.playlist_tracks(self.playlist_uri)['items']
        self.tracks_uri = [
            tracks[n]['track']['uri'] for n in range(len(tracks))
        ]

        if random_sample:
            self.seeds = sample(self.tracks_uri, 5)
        else:
            self.seeds = self.tracks_uri[:5]

        recommendations = self.recommendations(seed_tracks=self.seeds,
                                               limit=n_recoms)['tracks']
        self.recommendations_uri = [
            recommendations[n]['uri'] for n in range(len(recommendations))
        ]

        return self.recommendations_uri


    def create_custom_playlist(self, mood='DEU BOA!', public=True,
                               collaborative=False):
        if not self.recommendations_uri:
            self.recommendations_uri = self.get_recomendations_uri()

        self.playlist_uri = self.user_playlist_create(self.user_id, mood,
                                                      public=public,
                                                      collaborative=collaborative)['uri']

        self.playlist_add_items(self.playlist_uri, self.recommendations_uri)
>>>>>>> 9858caa6ecbe4ddb28b5ca7be6898641583047a6



if __name__ == '__main__':
<<<<<<< HEAD
    get_env_vars()
    sp = authorize_spotify()
    pl_uri = get_playlist_uri(sp)
    recom = get_recommendations_uri(sp, pl_uri)
    create_custom_playlist(sp, recom)
=======
    sp = MusicPlayer()
    sp.create_custom_playlist()
>>>>>>> 9858caa6ecbe4ddb28b5ca7be6898641583047a6
    print('GREAT SUCCESS!')
