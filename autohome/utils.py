from PIL import Image
from io import BytesIO
import base64
import numpy as np
from deepface.basemodels import Facenet
from scipy.spatial.distance import cosine


def pil_image_to_base64(pil_image):
    buf = BytesIO()
    pil_image.save(buf, format="JPEG")
    return base64.b64encode(buf.getvalue())


def base64_to_pil_image(base64_img):
    return Image.open(BytesIO(base64.b64decode(base64_img)))


def pil_image_to_array(pil_image):
    input_img = base64_to_pil_image(pil_image)
    return np.array(input_img)


def array_to_base64(img_array):
    im_pil = Image.fromarray(img_array)
    output_str = pil_image_to_base64(im_pil)
    return output_str.decode('ascii')

def get_gender(prob):
    if prob < 0.5:
        return "Male"
    else:
        return "Women"

def get_age(distr):
    if distr >= 0 and distr < 5:return "Baby"
    if distr >= 5 and distr < 12:return "Child"
    if distr >= 12 and distr < 18:return "Teenager"
    if distr >= 18 and distr < 25:return "Young Adult"
    if distr >= 25 and distr < 45: return "Adult"
    if distr >= 45 and distr <= 60: return "Middle Age"
    return "Old"

def get_emotion(emotion):
    if emotion == 0: return "Angry"
    if emotion == 1: return "Happy"
    if emotion == 2: return "Sad"
    if emotion == 3: return "Neutral"

def load_model_recognition():
    model = Facenet.InceptionResNetV2(dimension = 512)
    model.load_weights('./autohome/models/facenet512_weights.h5')
    return model

def load_saves():
    marcos = np.load(r'autohome/models/marcos.npy')
    adriel = np.load(r'autohome/models/adriel.npy')
    vitor = np.load(r'autohome/models/vitor.npy')
    return marcos, adriel, vitor

def recognition(pred_recognition, marcos, adriel, vitor):
    if cosine(pred_recognition, marcos) < 0.4:
        text = 'Marcos'
    elif cosine(pred_recognition, adriel) < 0.4:
        text = 'Adriel'
    elif cosine(pred_recognition, vitor) < 0.4:
        text = 'Vitor'
    else:
        text = 'Unknown'
    return text
