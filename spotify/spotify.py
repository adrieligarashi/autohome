import spotipy

from random import sample
from spotipy.oauth2 import SpotifyOAuth
from dotenv import find_dotenv, load_dotenv

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


def create_custom_playlist(sp,
                           recommendations_uri,
                           mood='FALA JÃO!',
                           public=True,
                           collaborative=False):

    user_id = sp.current_user()['id']

    playlist_uri = sp.user_playlist_create(user_id, mood, public=public,
                                           collaborative=collaborative)['uri']

    sp.playlist_add_items(playlist_uri, recommendations_uri)



if __name__ == '__main__':
    get_env_vars()
    sp = authorize_spotify()
    pl_uri = get_playlist_uri(sp)
    recom = get_recommendations_uri(sp, pl_uri)
    create_custom_playlist(sp, recom)
    print('GREAT SUCCESS!')
