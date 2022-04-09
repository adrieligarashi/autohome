import numpy as np
import cv2
from tensorflow.keras import models
from keras.models import load_model
import joblib

loaded_model = load_model('model.h5')
loaded_model_gender = load_model('model_gender.h5')
loaded_model_ethiny = load_model('model_ethiny.h5')
loaded_model_age = load_model('model_age.h5')


face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

cap = cv2.VideoCapture(0)
import copy

while True:

    ret, frame = cap.read()
    img = copy.deepcopy(frame)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x, y, w, h) in faces:
        fc = gray[y:y + h, x:x + w]

        roi = cv2.resize(fc, (48, 48))

        pred = loaded_model.predict(roi[np.newaxis, :, :, np.newaxis])
        pred_gender = loaded_model_gender.predict(roi[np.newaxis, :, :, np.newaxis])
        pred_ethiny = loaded_model_ethiny.predict(roi[np.newaxis, :, :, np.newaxis])
        pred_age = loaded_model_age.predict(roi[np.newaxis, :, :, np.newaxis])


        text_idx = np.argmax(pred)
        text_list = ['Angry', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad', 'Surprise']
        text_idx_gender = np.argmax(pred_gender)
        text_list_gender = ['Men', 'Women']
        text_idx_ethiny = np.argmax(pred_ethiny)
        text_list_ethiny = ['White', 'Black', 'Asian', 'Indian', 'Others']
        text_idx_age = np.argmax(pred_age)
        text_list_age = ['Baby', 'Teen', 'Teenager', 'Young_Adult', 'Adult', 'Old']

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

        cv2.putText(img, text, (x, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 255), 2)
        cv2.putText(img, text_gender, (x + w-10, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 255), 2)
        cv2.putText(img, text_ethiny, (x, y + h - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 255), 2)
        cv2.putText(img, text_age, (x + w-10, y + h - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 0, 255), 2)

        img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)

    cv2.imshow("frame", img)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
