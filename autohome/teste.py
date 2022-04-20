from flask import Flask, render_template
from flask_cors import CORS, cross_origin
from autohome.music_player import MusicPlayer

app = Flask(__name__)
CORS(app, origins=["http://127.0.0.1:5000/"])

mood = 'happy'

sp = MusicPlayer(mood=mood)
uri, url = sp.create_custom_playlist()
id = sp.get_device_id()
token = sp.auth.get_cached_token()['access_token']



@app.route('/')
def index():
    return render_template(
        'apiSpotify.html',
        playlist=uri,
        token=token,
        id=id
    )
