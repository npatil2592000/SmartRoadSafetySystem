import cv2
import os
from django.conf import settings
import numpy as np
import dlib
from imutils import face_utils
from pygame import mixer
import datetime
import pytz
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from PIL import Image
import pickle

class VideoCamera(object):
    def __init__(self):
        self.video=cv2.VideoCapture(0)
        self.classes = { 0:'Speed limit (20km/h)',
            1:'Speed limit (30km/h)', 
            2:'Speed limit (50km/h)', 
            3:'Speed limit (60km/h)', 
            4:'Speed limit (70km/h)', 
            5:'Speed limit (80km/h)', 
            6:'End of speed limit (80km/h)', 
            7:'Speed limit (100km/h)', 
            8:'Speed limit (120km/h)', 
            9:'No passing', 
            10:'No passing veh over 3.5 tons', 
            11:'Right-of-way at intersection', 
            12:'Priority road', 
            13:'Yield', 
            14:'Stop', 
            15:'No vehicles', 
            16:'Veh > 3.5 tons prohibited', 
            17:'No entry', 
            18:'General caution', 
            19:'Dangerous curve left', 
            20:'Dangerous curve right', 
            21:'Double curve', 
            22:'Bumpy road', 
            23:'Slippery road', 
            24:'Road narrows on the right', 
            25:'Road work', 
            26:'Traffic signals', 
            27:'Pedestrians', 
            28:'Children crossing', 
            29:'Bicycles crossing', 
            30:'Beware of ice/snow',
            31:'Wild animals crossing', 
            32:'End speed + passing limits', 
            33:'Turn right ahead', 
            34:'Turn left ahead', 
            35:'Ahead only', 
            36:'Go straight or right', 
            37:'Go straight or left', 
            38:'Keep right', 
            39:'Keep left', 
            40:'Roundabout mandatory', 
            41:'End of no passing', 
            42:'End no passing veh > 3.5 tons' }
        self.model=load_model((os.path.join(settings.BASE_DIR,"traffic_sign_detector/traffic_sign_detection.h5")))

    def __del__(self):
        self.video.release() 

    def get_frame(self,request):
        _, frame = self.video.read()
        image_fromarray = Image.fromarray(frame, 'RGB')
        resize_image = image_fromarray.resize((30, 30))
        expand_input = np.expand_dims(resize_image,axis=0)
        input_data = np.array(expand_input)
        # input_data = input_data/255
        pred = self.classes[np.argmax(self.model.predict(input_data))]
        cv2.putText(frame, pred, (100,100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,255,0),3)
        cv2.imencode('.jpg', frame)
        # print(pred)
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()