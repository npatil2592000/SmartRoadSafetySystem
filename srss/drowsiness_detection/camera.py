import cv2
import os
from django.conf import settings
import numpy as np
import dlib
from imutils import face_utils
from pygame import mixer
import datetime
from .models import drowsiness_history
import pytz

class VideoCamera(object):
    def __init__(self):
        self.video=cv2.VideoCapture(0)
        # (self.grabbed, self.frame) = self.video.read()
        # threading.Thread(target=self.update, args=()).start()
        self.sleep=0
        self.drowsy=0
        self.active=0
        self.status=""
        self.color=(0,0,0)
        self.flag=0
        self.cnt=0
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(os.path.join(settings.BASE_DIR,"landmarks\shape_predictor_68_face_landmarks.dat"))#************
    def __del__(self):
        mixer.music.stop()
        self.video.release() 

    def compute(self,ptA,ptB):
        dist = np.linalg.norm(ptA - ptB)
        return dist

    def blinked(self,a,b,c,d,e,f):
        up = self.compute(b,d) + self.compute(c,e)
        down = self.compute(a,f)
        ratio = up/(2.0*down)

        #Checking if it is blinked
        if(ratio>0.25):
            return 2
        elif(ratio>0.21 and ratio<=0.25):
            return 1
        else:
            return 0

    def get_frame(self,request):
        # success, cap = self.video.read()
		# We are using Motion JPEG, but OpenCV defaults to capture raw images,
		# so we must encode it into JPEG in order to correctly display the
		# video stream.
        self.cnt+=1
        # p = multiprocessing.Process(target=playsound, args=(os.path.join(settings.BASE_DIR,"landmarks\siren.mp3"),))
        mixer.init()
        # detector = dlib.get_frontal_face_detector
    #     detector = dlib.get_frontal_face_detector()
    #     predictor = dlib.shape_predictor(os.path.join(settings.BASE_DIR,"landmarks\shape_predictor_68_face_landmarks.dat"))#************oin(settings.BASE_DIR,"landmarks\shape_predictor_68_face_landmarks.dat"))#************
        # while True:
        _, frame = self.video.read()
        face_frame=frame.copy()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = self.detector(gray)
        #detected face in faces array
        for face in faces:
            x1 = face.left()
            y1 = face.top()
            x2 = face.right()
            y2 = face.bottom()

            face_frame = frame.copy()
            cv2.rectangle(face_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            landmarks = self.predictor(gray, face)                
            landmarks = face_utils.shape_to_np(landmarks)

            #The numbers are actually the landmarks which will show eye
            left_blink = self.blinked(landmarks[36],landmarks[37], 
                landmarks[38], landmarks[41], landmarks[40], landmarks[39])
            right_blink = self.blinked(landmarks[42],landmarks[43], 
                landmarks[44], landmarks[47], landmarks[46], landmarks[45])
            
            #Now judge what to do for the eye blinks
            if(left_blink==0 or right_blink==0):
                self.sleep+=1
                self.drowsy=0
                self.active=0
                if(self.sleep>6):
                    self.status="SLEEPING !!!"
                    self.color = (255,0,0)
                    if(self.flag==0):
                        # p = multiprocessing.Process(target=playsound, args=(os.path.join(settings.BASE_DIR,"landmarks\siren.mp3"),))
                        # p.start()
                        time=datetime.datetime.now()
                        t=datetime.datetime(time.year,time.month,time.day,time.hour,time.minute,time.second,time.microsecond, tzinfo=pytz.UTC)
                        data=drowsiness_history(USERNAME=request.user.username,NAME=request.user.first_name+request.user.last_name,EMAIL=request.user.email,TIME=t)
                        data.save()
                        print("alarm raised1 flag: ",self.flag)
                        mixer.music.load(os.path.join(settings.BASE_DIR,"landmarks\siren.mp3"))
                        mixer.music.play()
                        self.flag=1

            elif(left_blink==1 or right_blink==1):
                self.sleep=0
                self.active=0
                self.drowsy+=1
                print(self.drowsy,"drowsy")
                if(self.drowsy>6):
                    self.status="Drowsy !"
                    self.color = (0,0,255)
                    if(self.flag==0):
                        # p = multiprocessing.Process(target=playsound, args=("siren.mp3",))
                        # p.start()
                        time=datetime.datetime.now()
                        t=datetime.datetime(time.year,time.month,time.day,time.hour,time.minute,time.second,time.microsecond, tzinfo=pytz.UTC)
                        data=drowsiness_history(USERNAME=request.user.username,NAME=request.user.first_name+request.user.last_name,EMAIL=request.user.email,TIME=t)
                        data.save()
                        print("alarm raised2 flag: ",self.flag)
                        mixer.music.load(os.path.join(settings.BASE_DIR,"landmarks\siren.mp3"))
                        mixer.music.play()
                        self.flag=1

            else:
                self.drowsy=0
                self.sleep=0
                self.active+=1
                print(self.active,"active")
                if(self.active>6):
                    print("ACTIVE!!")
                    self.status="Active :)"
                    self.color = (0,255,0)
                    if(self.flag==1):
                        # p.terminate()
    #         			p = multiprocessing.Process(target=playsound, args=("siren.mp3",))
                        print("alarm stopped")
                        mixer.music.stop()
                        self.flag=0
            cv2.putText(frame, self.status, (100,100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, self.color,3)
            # print(self.status,self.cnt)
            # for n in range(0, 68):
            #     (x,y) = landmarks[n]
            #     cv2.circle(face_frame, (x, y), 1, (255, 255, 255), -1)

        # cv2.imshow("Frame", frame)
        # cv2.imshow("Result of detector", face_frame)
        # key = cv2.waitKey(1)
        # if key == 27:
        #     break
        # frame_flip = cv2.flip(frame,1)
        ret, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()