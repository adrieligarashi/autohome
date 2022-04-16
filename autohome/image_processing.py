from autohome.utils import pil_image_to_array, base64_to_pil_image, array_to_base64
import copy
from facenet_pytorch import MTCNN
import cv2
import numpy as np
from keras.models import load_model
from keras.applications.xception import preprocess_input

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

pred_passadas = np.array([np.zeros(40) for x in range(0, 7)])
pred_mean = np.array([0, 0, 0, 0, 0, 0, 0])
pred = np.array([0, 0, 0, 0, 0, 0, 1])
n_mean = 1

loaded_model = load_model('autohome/models/trained_vggface.h5')
# loaded_model_gender = load_model('autohome/models/model_gender.h5')
loaded_model_gender = load_model('autohome/models/gender_test.hdf5')
# loaded_model_ethiny = load_model('autohome/models/model_ethiny.h5')
# loaded_model_age = load_model('autohome/models/model_age.h5')
loaded_model_age = load_model('autohome/models/age_prediction.h5')

mtcnn = MTCNN(image_size=224, margin=10, keep_all=True, min_face_size=40)


def image_proc(input):

    global pred_mean
    global n_mean
    global pred
    global pred_passadas

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
                # fc_gray = cv2.cvtColor(fc, cv2.COLOR_BGR2GRAY)

                # roi = cv2.resize(fc_gray, (48, 48))
                roi_face = cv2.resize(fc, (96, 96))

                roi_gender = cv2.resize(cv2.cvtColor(fc, cv2.COLOR_BGR2RGB),
                                        (178, 218))


                roi_age_temp = cv2.resize(fc, (224, 224))
                roi_age = preprocess_input(roi_age_temp)


                pred = loaded_model.predict(roi_face[np.newaxis, :, :])

                add_pred = np.insert(pred_passadas, 0, pred, axis=1)
                shifted_pred = np.delete(add_pred,
                                         add_pred.shape[1] - 1,
                                         axis=1)

                pred_passadas = shifted_pred.copy()
                pred_mean = np.mean(shifted_pred, axis=1)


                pred_resume = np.array([
                    pred_mean[0:3].max(), pred_mean[3], pred_mean[4],
                    pred_mean[5:7].max()
                ])



                # pred_gender = loaded_model_gender.predict(roi[np.newaxis, :, :,
                #                                               np.newaxis])
                pred_gender = loaded_model_gender.predict(roi_gender[np.newaxis, :, :])
                # pred_ethiny = loaded_model_ethiny.predict(roi[np.newaxis, :, :,
                #                                              np.newaxis])
                # pred_age = loaded_model_age.predict(roi[np.newaxis, :, :,
                #                                         np.newaxis])
                pred_age = loaded_model_age.predict(roi_age[np.newaxis, :, :])


                text_idx = np.argmax(pred_resume)
                # text_list = [
                #     'Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise',
                #     'Neutral'
                # ]
                text_list = [
                    'Angry', 'Happy', 'Sad', 'Neutral'
                ]
                # text_idx_gender = np.argmax(pred_gender)
                # text_list_gender = ['Men', 'Women']
                # text_idx_ethiny = np.argmax(pred_ethiny)
                # text_list_ethiny = [
                #     'White', 'Black', 'Asian', 'Indian', 'Others'
                # ]
                # text_idx_age = np.argmax(pred_age)
                # text_list_age = [
                #     'Baby', 'Teen', 'Teenager', 'Young_Adult', 'Adult', 'Old'
                # ]

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

                # if text_idx_gender == 0:
                #     text_gender = text_list_gender[0]
                # elif text_idx_gender == 1:
                #     text_gender = text_list_gender[1]

                text_gender = get_gender(pred_gender[0][0])

                # if text_idx_ethiny == 0:
                #     text_ethiny = text_list_ethiny[0]
                # if text_idx_ethiny == 1:
                #     text_ethiny = text_list_ethiny[1]
                # elif text_idx_ethiny == 2:
                #     text_ethiny = text_list_ethiny[2]
                # elif text_idx_ethiny == 3:
                #     text_ethiny = text_list_ethiny[3]
                # elif text_idx_ethiny == 4:
                #     text_ethiny = text_list_ethiny[4]

                # if text_idx_age == 0:
                #     text_age = text_list_age[0]
                # if text_idx_age == 1:
                #     text_age = text_list_age[1]
                # elif text_idx_age == 2:
                #     text_age = text_list_age[2]
                # elif text_idx_age == 3:
                #     text_age = text_list_age[3]
                # elif text_idx_age == 4:
                #     text_age = text_list_age[4]
                # elif text_idx_age == 5:
                #     text_age = text_list_age[5]

                text_age = get_age(pred_age[0])

                box = boxes[i]
                box = box.astype(int)

                cv2.putText(img, text_gender, (box[0] - 40, box[1] + 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 255), 2)
                cv2.putText(img, text_age, (box[0] + 70, box[1] + 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 255), 2)
                # cv2.putText(img, text_ethiny, (box[2] - 100, box[3]),
                #             cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 255), 2)
                cv2.putText(img, text, (box[2] - 50, box[3] + 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 255), 2)

                img = cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]),
                                    (255, 0, 0), 2)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    image_data = array_to_base64(img)
    return image_data, pred_resume, text_list, text
