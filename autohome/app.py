import re
from sys import stdout
from autohome.process import webopencv
import logging
from flask import Flask, render_template, Response, request, jsonify, redirect, session
from flask_session import Session
from flask_socketio import SocketIO, emit
from autohome.camera import Camera
from autohome.image_processing import image_proc
import numpy as np
from autohome.music_player import MusicPlayer
from autohome.mqtt import mqtt_publish
from autohome.news_analysis import News
from autohome.auth_backup.oauth2 import SpotifyOAuth
from dotenv import find_dotenv, load_dotenv
import uuid
import spotipy
import os


env_path = find_dotenv()
load_dotenv(env_path)

pred_resume = np.array([0, 0, 0, 0.1])
text_list = [
    'Angry', 'Happy', 'Sad', 'Neutral'
]
text = ''
felling_spotify = '?'
text_recognition = '?'
na_casa = 0
sp = ''
uri = ''
token = ''
titles = ['Waiting for you to get home', 'Waiting for you to get home',
            'Waiting for you to get home']
texts = ['Waiting for you to get home', 'Waiting for you to get home',
            'Waiting for you to get home']
urls = ['/run', '/run', '/run']

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(stdout))
app.config['SECRET_KEY'] = os.urandom(64)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = './.flask_session/'
app.config['DEBUG'] = True
Session(app)
socketio = SocketIO(app)
camera = Camera(webopencv())


client = mqtt_publish.connect_mqtt()
client.loop_start()

news = News()
n_news = 7

positive_news, neutral_news, negative_news = news.get_news_by_sentiment(n=n_news)


caches_folder = './app/users/'
if not os.path.exists(caches_folder):
    os.makedirs(caches_folder)

def session_cache_path():
    return caches_folder + session.get('uuid')


@socketio.on('input image', namespace='/test')
def test_message(input):
    global pred_resume
    global text_list
    global text, text_recognition

    input = input.split(",")[1]
    camera.enqueue_input(input)
    image_data, pred_resume, text_list, text, text_recognition = image_proc(
        input)

    image_data = "data:image/jpeg;base64," + image_data
    emit('out-image-event', {'image_data': image_data}, namespace='/test')


@socketio.on('connect', namespace='/test')
def test_connect():
    app.logger.info("client connected")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/run', methods=['GET', 'POST'])
def run():
    global na_casa
    global felling_spotify
    global uri
    global token, text, sp, text_recognition
    global titles
    global texts
    global urls

    clicks = {}
    front_news = []

    if not session.get('uuid'):
        session['uuid'] = str(uuid.uuid4())

    scope = 'playlist-read-private,user-modify-playback-state,user-read-playback-state,user-read-currently-playing,app-remote-control,streaming,playlist-modify-public,playlist-modify-private'

    cache_handler = spotipy.cache_handler.CacheFileHandler(cache_path=session_cache_path())
    auth_manager = SpotifyOAuth(scope=scope, cache_handler=cache_handler, show_dialog=True)

    if request.args.get('code'):
        auth_manager.get_access_token(request.args.get('code'))
        return redirect('/run')

    if not auth_manager.validate_token(cache_handler.get_cached_token()):
        auth_url = auth_manager.get_authorize_url()
        return redirect(auth_url)


    if request.method == 'POST':
        na_casa = request.form.get('botaocasa')
        print(na_casa, type(na_casa))

        sp = MusicPlayer(auth_manager)

        if na_casa == '1':
            felling_spotify = text
            uri = sp.create_custom_playlist(mood=felling_spotify)
            token = auth_manager.get_cached_token()['access_token']
            # mqtt_publish.publish(client,
            #                      topic='le_wagon_769',
            #                      msg=f"{felling_spotify}, {text_recognition}")

            sp.clear_instance()


            if felling_spotify.lower() == 'happy' or felling_spotify.lower() == 'neutral':
                for article in positive_news:
                    try:
                        front_news.append(article)
                    except:
                        continue
                    if len(front_news) >= 3:
                        break

                for article in neutral_news:
                    try:
                        front_news.append(article)
                    except:
                        continue
                    if len(front_news) >= 3:
                        break

                for article in negative_news:
                    try:
                        front_news.append(article)
                    except:
                        continue
                    if len(front_news) >= 3:
                        break


            if felling_spotify.lower() == 'sad' or felling_spotify.lower() == 'angry':
                for article in positive_news:
                    try:
                        front_news.append(article)
                    except:
                        continue
                    if len(front_news) >= 3:
                        break

                for article in neutral_news:
                    try:
                        front_news.append(article)
                    except:
                        continue
                    if len(front_news) >= 3:
                        break

            while len(front_news) < 3:
                place_holder = {'title': 'Não tem notícia pra você hoje.',
                                'text': 'Desculpe, mas não tenho uma notícia apropriada para você hoje.',
                                'url': '/'}
                front_news.append(place_holder)


            try:
                titles = [article['title'] for article in front_news]
                texts = [article['text'] for article in front_news]
                urls = [article['url'] for article in front_news]
            except:
                print('titulos quebrados')
                print(front_news)
                print(titles)


        try:
            clicks = request.get_json()
        except:
            print('nao deu ainda clicked getjson')

        if clicks is not None:

            uri = sp.create_custom_playlist(mood=felling_spotify)
            token = sp.auth.get_cached_token()['access_token']

            if clicks['clicked'] == '1':
                proper_new = texts[0]
            elif clicks['clicked'] == '2':
                proper_new = texts[1]
            elif clicks['clicked'] == '3':
                proper_new = texts[2]


            resume = news.get_text_resume(proper_new)
            # mqtt_publish.publish(client,
            #                      topic='le_wagon_769_news',
            #                      msg=f"{resume}")

            sp.clear_instance()


    return render_template('run.html',
                        values=pred_resume.tolist(),
                        labels=text_list,
                        felling_spotify = felling_spotify,
                        playlist=uri,
                        token=token,
                        text_recognition=text_recognition,
                        titles=titles,
                        urls=urls)


@app.route('/data', methods=['GET'])
def data():
    return jsonify(result=pred_resume.tolist())


def gen():
    """Video streaming generator function."""

    app.logger.info("starting to generate frames!")
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')



################################ MENUS ###########################
@app.route('/dataengineering')
def dataengineering():
    return render_template('dataengineering.html')


@app.route('/flowchart')
def flowchart():
    return render_template('flowchart.html')


@app.route('/linkedin')
def linkedin():
    return render_template('linkedin.html')


@app.route('/scope')
def scope():
    return render_template('scope.html')


@app.route('/technologies')
def technologies():
    return render_template('technologies.html')


@app.route('/theteam')
def theteam():
    return render_template('theteam.html')


@app.route('/solutions')
def solutions():
    return render_template('solutions.html')
##################################################################


if __name__ == '__main__':
    socketio.run(app, debug=True)
