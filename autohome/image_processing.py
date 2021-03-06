from autohome.utils import pil_image_to_array, array_to_base64, get_age, get_gender, get_emotion,\
    load_model_recognition, load_saves, recognition
import copy
import cv2
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.xception import preprocess_input
from autohome.FastMTCNN import FastMTCNN
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

marcos, adriel, vitor = load_saves()

# device = 'cuda' if torch.cuda.is_available() else 'cpu'
device = 'cpu'
fast_mtcnn = FastMTCNN(stride=4,
                       resize=1,
                       margin=30,
                       factor=0.8,
                       keep_all=True,
                       device=device)


pred_passadas = np.array([np.zeros(10) for x in range(0, 7)])
pred_mean = np.array([0, 0, 0, 0, 0, 0, 0])
pred = np.array([0, 0, 0, 0, 0, 0, 0.1])
n_mean = 1
pred_resume = np.array([0, 0, 0, 0.1])


loaded_model = load_model('autohome/models/trained_vggface.h5')
loaded_model_gender = load_model('autohome/models/model_gender.h5')
loaded_model_age = load_model('autohome/models/age_prediction.h5')

model_recognition = load_model_recognition()


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
    text_recognition = 'Unknown'

    open_cv_image = pil_image_to_array(input)
    open_cv_image = open_cv_image[:, :, ::-1].copy()

    img = copy.deepcopy(open_cv_image)

    # img_cropped_list, prob_list = mtcnn(base64_to_pil_image(input),
    #                                     return_prob=True)

    faces, boxes, probs = fast_mtcnn([img])

    if faces is not None and type(faces) is not type(None):

        #boxes, _ = mtcnn.detect(base64_to_pil_image(input))
        for i, prob in enumerate(probs[0]):  #enumerate(prob_list):
            if prob is not None and prob > 0.60 and type(
                    faces[i]) is not type(None):
                #fc = faces[i].permute(1, 2, 0).numpy()


                fc = faces[i]
                fc = fc[:, :, ::-1].copy()

                roi_face = cv2.resize(fc, (96, 96))
                roi_gender = cv2.resize(cv2.cvtColor(fc, cv2.COLOR_BGR2GRAY),
                                        (48, 48))

                roi_age_temp = cv2.resize(fc, (224, 224))
                roi_age = preprocess_input(roi_age_temp)

                roi_recognition = cv2.resize(fc, (160, 160))
                roi_recognition_new = preprocess_input(roi_recognition[np.newaxis, :, :])


                pred = loaded_model.predict(roi_face[np.newaxis, :, :])

                add_pred = np.insert(pred_passadas, 0, pred, axis=1)
                shifted_pred = np.delete(add_pred,
                                            add_pred.shape[1] - 1,
                                            axis=1)

                pred_passadas = shifted_pred.copy()
                # print(pred_passadas)
                pred_mean = np.mean(shifted_pred, axis=1)


                pred_resume = np.array([
                    pred_mean[0:3].max(), pred_mean[3], pred_mean[4],
                    pred_mean[6:7].max()
                ])

                # print(pred_resume)

                pred_gender = loaded_model_gender.predict(roi_gender[np.newaxis, :, :])
                pred_age = loaded_model_age.predict(roi_age[np.newaxis, :, :])
                pred_recognition = model_recognition.predict(roi_recognition_new)


                text = get_emotion(np.argmax(pred_resume))
                text_gender = get_gender(pred_gender[0][0])
                text_age = get_age(pred_age[0])
                text_recognition = recognition(pred_recognition[0], marcos, adriel, vitor)


                box = boxes[0][i]
                box = box.astype(int)

                cv2.putText(img, text_gender, (box[0] - 40, box[1] + 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 255), 2)
                cv2.putText(img, text_age, (box[0] + 70, box[1] + 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 255), 2)
                cv2.putText(img, text_recognition, (box[2] - 100, box[3] + 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 255), 2)
                cv2.putText(img, text, (box[2] + 20, box[3] + 10),

                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 255), 2)

                img = cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]),
                                    (255, 0, 0), 2)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    image_data = array_to_base64(img)
    return image_data, pred_resume, text_list, text, text_recognition
