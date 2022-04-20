from autohome.utils import pil_image_to_array, array_to_base64, get_age, get_gender, get_emotion
import copy
import cv2
import numpy as np
from keras.models import load_model
from keras.applications.xception import preprocess_input
from autohome.FastMTCNN import FastMTCNN
import torch

device = 'cuda' if torch.cuda.is_available() else 'cpu'

fast_mtcnn = FastMTCNN(stride=4,
                       resize=1,
                       margin=30,
                       factor=0.9,
                       keep_all=True,
                       device=device)


pred_passadas = np.array([np.zeros(40) for x in range(0, 7)])
pred_mean = np.array([0, 0, 0, 0, 0, 0, 0])
pred = np.array([0, 0, 0, 0, 0, 0, 1])
n_mean = 1
pred_resume = np.array([0, 0, 0, 1])

loaded_model = load_model('autohome/models/trained_vggface.h5')
# loaded_model_gender = load_model('autohome/models/model_gender.h5')
loaded_model_gender = load_model('autohome/models/model_gender.h5')
# loaded_model_ethiny = load_model('autohome/models/model_ethiny.h5')
# loaded_model_age = load_model('autohome/models/model_age.h5')
loaded_model_age = load_model('autohome/models/age_prediction.h5')

#mtcnn = MTCNN(image_size=224, margin=10, keep_all=True, min_face_size=40)


def image_proc(input):

    global pred_mean
    global n_mean
    global pred
    global pred_passadas
    global pred_resume

    text_list = [
    'Angry', 'Happy', 'Sad', 'Neutral'
    ]
    text = 'Neutral'

    open_cv_image = pil_image_to_array(input)
    open_cv_image = open_cv_image[:, :, ::-1].copy()

    img = copy.deepcopy(open_cv_image)

    # img_cropped_list, prob_list = mtcnn(base64_to_pil_image(input),
    #                                     return_prob=True)

    faces, boxes, probs = fast_mtcnn([img])

    if faces is not None:
        #boxes, _ = mtcnn.detect(base64_to_pil_image(input))
        for i, prob in enumerate(probs[0]):  #enumerate(prob_list):

            if prob is not None and prob > 0.60:
                #fc = faces[i].permute(1, 2, 0).numpy()

                fc = faces[i]
                fc = fc[:, :, ::-1].copy()

                # fc_gray = cv2.cvtColor(fc, cv2.COLOR_BGR2GRAY)

                # roi = cv2.resize(fc_gray, (48, 48))
                roi_face = cv2.resize(fc, (96, 96))

                roi_gender = cv2.resize(cv2.cvtColor(fc, cv2.COLOR_BGR2GRAY),
                                        (48, 48))


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


                text = get_emotion(np.argmax(pred_resume))
                text_gender = get_gender(pred_gender[0][0])
                text_age = get_age(pred_age[0])

                box = boxes[0][i]
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
