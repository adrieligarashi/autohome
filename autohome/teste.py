from flask import Flask, render_template
from autohome.music_player import MusicPlayer

app = Flask(__name__)

mood = 'angry'

sp = MusicPlayer(mood=mood)
uri, url = sp.create_custom_playlist()
token = sp.auth.get_cached_token()['access_token']



@app.route('/')
def index():
    return render_template(
        'apiSpotify.html',
        playlist=uri,
        token=token
    )
