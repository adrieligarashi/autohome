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
