from autohome.utils import pil_image_to_array, base64_to_pil_image, array_to_base64
import copy
from facenet_pytorch import MTCNN
import cv2
import numpy as np
from keras.models import load_model

pred_mean = np.array([0, 0, 0, 0, 0, 0, 0])
pred = np.array([0, 0, 0, 0, 0, 0, 1])
n_mean = 1

loaded_model = load_model('autohome/models/trained_vggface.h5')
loaded_model_gender = load_model('autohome/models/model_gender.h5')
loaded_model_ethiny = load_model('autohome/models/model_ethiny.h5')
loaded_model_age = load_model('autohome/models/model_age.h5')

mtcnn = MTCNN(image_size=240, margin=0, keep_all=True, min_face_size=40)

def image_proc(input):

    global pred_mean
    global n_mean
    global pred

    open_cv_image = pil_image_to_array(input)
    open_cv_image = open_cv_image[:, :, ::-1].copy()

    img = copy.deepcopy(open_cv_image)

    img_cropped_list, prob_list = mtcnn(base64_to_pil_image(input),
                                        return_prob=True)

    if img_cropped_list is not None:
        boxes, _ = mtcnn.detect(base64_to_pil_image(input))
        for i, prob in enumerate(prob_list):
            if prob > 0.80:

                fc = img_cropped_list[i].permute(1, 2, 0).numpy()
                fc = fc[:, :, ::-1].copy()
                fc_gray = cv2.cvtColor(fc, cv2.COLOR_BGR2GRAY)

                roi = cv2.resize(fc_gray, (48, 48))
                roi_face = cv2.resize(fc, (96, 96))

                if n_mean == 5:
                    pred = pred_mean
                    pred_mean = pred_mean / n_mean
                    n_mean = 1
                else:
                    n_mean += 1
                    pred_mean = pred_mean + loaded_model.predict(
                        roi_face[np.newaxis, :, :])



                pred_gender = loaded_model_gender.predict(roi[np.newaxis, :, :,
                                                              np.newaxis])
                pred_ethiny = loaded_model_ethiny.predict(roi[np.newaxis, :, :,
                                                              np.newaxis])
                pred_age = loaded_model_age.predict(roi[np.newaxis, :, :,
                                                        np.newaxis])

                text_idx = np.argmax(pred)
                text_list = [
                    'Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise',
                    'Neutral'
                ]
                text_idx_gender = np.argmax(pred_gender)
                text_list_gender = ['Men', 'Women']
                text_idx_ethiny = np.argmax(pred_ethiny)
                text_list_ethiny = [
                    'White', 'Black', 'Asian', 'Indian', 'Others'
                ]
                text_idx_age = np.argmax(pred_age)
                text_list_age = [
                    'Baby', 'Teen', 'Teenager', 'Young_Adult', 'Adult', 'Old'
                ]

                if text_idx == 0:
                    text = text_list[0]
                if text_idx == 1:
                    text = text_list[1]
                elif text_idx == 2:
                    text = text_list[2]
                elif text_idx == 3:
                    text = text_list[3]
                elif text_idx == 4:
                    text = text_list[4]
                elif text_idx == 5:
                    text = text_list[5]
                elif text_idx == 6:
                    text = text_list[6]

                if text_idx_gender == 0:
                    text_gender = text_list_gender[0]
                elif text_idx_gender == 1:
                    text_gender = text_list_gender[1]

                if text_idx_ethiny == 0:
                    text_ethiny = text_list_ethiny[0]
                if text_idx_ethiny == 1:
                    text_ethiny = text_list_ethiny[1]
                elif text_idx_ethiny == 2:
                    text_ethiny = text_list_ethiny[2]
                elif text_idx_ethiny == 3:
                    text_ethiny = text_list_ethiny[3]
                elif text_idx_ethiny == 4:
                    text_ethiny = text_list_ethiny[4]

                if text_idx_age == 0:
                    text_age = text_list_age[0]
                if text_idx_age == 1:
                    text_age = text_list_age[1]
                elif text_idx_age == 2:
                    text_age = text_list_age[2]
                elif text_idx_age == 3:
                    text_age = text_list_age[3]
                elif text_idx_age == 4:
                    text_age = text_list_age[4]
                elif text_idx_age == 5:
                    text_age = text_list_age[5]
                box = boxes[i]
                box = box.astype(int)

                cv2.putText(img, text, (box[0] - 50, box[1]),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 255), 2)
                cv2.putText(img, text_gender, (box[0] + 60, box[1]),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 255), 2)
                cv2.putText(img, text_ethiny, (box[2] - 100, box[3]),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 255), 2)
                cv2.putText(img, text_age, (box[2] + 5, box[3] + 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 255), 2)

                img = cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]),
                                    (255, 0, 0), 2)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    image_data = array_to_base64(img)
    return image_data, pred, text_list
