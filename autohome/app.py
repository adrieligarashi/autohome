from sys import stdout
from autohome.process import webopencv
import logging
from flask import Flask, render_template, Response, request, jsonify
from flask_socketio import SocketIO, emit
from autohome.camera import Camera
from autohome.image_processing import image_proc
import numpy as np
from autohome.music_player import MusicPlayer
from autohome.mqtt import mqtt_publish


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


app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(stdout))
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True
socketio = SocketIO(app)
camera = Camera(webopencv())

client = mqtt_publish.connect_mqtt()
client.loop_start()


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
    global sp

    sp = MusicPlayer()

    return render_template('index.html')


@app.route('/run', methods=['GET', 'POST'])
def run():
    global na_casa
    global felling_spotify
    global uri
    global token, text, sp, text_recognition

    if request.method == 'POST':
        na_casa = request.form.get('botaocasa')
        print(na_casa, type(na_casa))

        if na_casa == '1':
            felling_spotify = text
            uri, _ = sp.create_custom_playlist(mood=felling_spotify)
            token = sp.auth.get_cached_token()['access_token']
            mqtt_publish.publish(client,
                                 topic='le_wagon_769',
                                 msg=f"{felling_spotify}, {text_recognition}")
            na_casa = 0

    return render_template('run.html',
                        values=pred_resume.tolist(),
                        labels=text_list,
                        felling_spotify = felling_spotify,
                        playlist=uri,
                        token=token,
                        text_recognition=text_recognition)


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
