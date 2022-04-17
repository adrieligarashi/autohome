from PIL import Image
from io import BytesIO
import base64
import numpy as np


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
