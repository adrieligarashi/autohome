from cProfile import label
import json
from sys import stdout
from urllib import response
from autohome.process import webopencv
import logging
from flask import Flask, render_template, Response, request, jsonify
from flask_socketio import SocketIO, emit
from autohome.camera import Camera
from autohome.image_processing import image_proc
import numpy as np

pred_resume = np.array([0, 0, 0, 1])
text_list = [
    'Angry', 'Happy', 'Sad', 'Neutral'
]



app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(stdout))
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True
socketio = SocketIO(app)
camera = Camera(webopencv())




@socketio.on('input image', namespace='/test')
def test_message(input):
    global pred_resume
    global text_list

    input = input.split(",")[1]
    camera.enqueue_input(input)
    #image_data = input  # Do your magical Image processing here!!
    #image_data = image_data.decode("utf-8")
    #print("IMG_DATA_DECODEDE", type(image_data))

    image_data, pred_resume, text_list, text = image_proc(input)

    # print('IMG_DATA', type(image_data))

    image_data = "data:image/jpeg;base64," + image_data
    # print("OUTPUT " + image_data)
    emit('out-image-event', {'image_data': image_data}, namespace='/test')
    #camera.enqueue_input(base64_to_pil_image(input))


@socketio.on('connect', namespace='/test')
def test_connect():
    app.logger.info("client connected")


@app.route('/')
def index():
    """Video streaming home page."""
    return render_template('index.html',
                           values=pred_resume.tolist(),
                           labels=text_list)


@app.route('/data', methods=['GET'])
def data():
    # response = make_response(json.dumps(pred.tolist()))
    # response.content_type = 'application/json'
    return jsonify(result=pred_resume.tolist())


def gen():
    """Video streaming generator function."""

    app.logger.info("starting to generate frames!")
    while True:
        frame = camera.get_frame()  #pil_image_to_base64(camera.get_frame())
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    socketio.run(app)
