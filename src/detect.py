import numpy as np
import cv2
from matplotlib import pyplot as plt
import time
import pygame.mixer

pygame.init()
pygame.mixer.music.load("beep-01a.wav")

#import pyglet
#music = pyglet.resource.media('beep-01a.wav')
#player = pyglet.media.Player()
#print dir(music)

face_cascade = cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascades2/haarcascade_eye.xml')

simulate_real_time = "true"

if(simulate_real_time == "true"):
    cap = cv2.VideoCapture(0)

process_eye = 0
eyeq_len = 5
eyeq = []

def push_val(val):
    if(val < 800):
        if len(eyeq) <= eyeq_len:
            eyeq.append(val)
        else:
            eyeq.append(val)
            eyeq.pop(0)
    return avg_eyeq()

def avg_eyeq():
    avg = 0
    for i in eyeq:
        avg = avg + i
    avg = avg / len(eyeq)
    
    return avg

def detect_and_draw(img, gray):
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    for (x,y,w,h) in faces:
        img = cv2.rectangle(img, (x,y),(x+w,y+h),(255,0,0),2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]
        eyes = eye_cascade.detectMultiScale(roi_gray)
        max_eyes = 2
        cnt_eye = 0
        for (ex,ey,ew,eh) in eyes:
            if(cnt_eye == max_eyes):
                break;
            
            image_name = 'Eye_' + str(cnt_eye)

            ex = ex + (ew/6)
            ew = ew - (ew/6)
            ey = ey + (eh/3)
            eh = eh/3
            
            cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),1)
            
            roi_eye_gray = roi_gray[ey:ey+eh, ex:ex+ew]
            roi_eye_color = roi_color[ey:ey+eh, ex:ex+ew]

            # create & normalize histogram ---------
            hist = cv2.calcHist([roi_eye_gray], [0],None, [256], [0,256])
            histn = []
            max_val = 0
            for i in hist:
                value = int(i[0])
                histn.append(value)
                if(value > max_val):
                    max_val = value
            for index, value in enumerate(histn):
                histn[index] = ((value * 256) / max_val)
            #print histn
            # normalize histogram ends ---------

            

            # Slice
            roi_eye_gray2 = roi_eye_gray.copy()
            #roi_eye_gray2 = cv2.threshold(roi_eye_gray2, 50, 255, cv2.THRESH_TOZERO)
            #roi_eye_gray2 = cv2.adaptiveThreshold(roi_eye_gray2, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 10)

            threshold = 65
            total_white = 0
            total_black = 0
            for i in range(0, roi_eye_gray2.shape[0]):
                for j in range(0, roi_eye_gray2.shape[1]):
                    pixel_value = roi_eye_gray2[i, j]
                    if(pixel_value >= threshold):
                        roi_eye_gray2[i, j] = 255
                        total_white = total_white + 1
                    else:
                        roi_eye_gray2[i, j] = 0
                        total_black = total_black + 1

            #cv2.imshow(image_name, roi_eye_gray2)
            if image_name == "Eye_0":
                ag = push_val(total_white)
            
            if(simulate_real_time == "true"):
                pass
                # put number on image
                if(cnt_eye == 0):
                    cv2.putText(img, ""+str(total_white), (10, 40), cv2.FONT_HERSHEY_PLAIN, 2, 255)
                else:
                    cv2.putText(img, ""+str(total_white), (520, 40), cv2.FONT_HERSHEY_PLAIN, 2, 255)
            else:
                plt.subplot(2,3,((cnt_eye*3)+1)),plt.hist(roi_eye_gray.ravel(), 256, [0,256])
                plt.title(image_name+' Hist')
                plt.subplot(2,3,((cnt_eye*3)+2)),plt.imshow(roi_eye_color, 'gray')
                plt.title(image_name+' Image Threshold')
                plt.subplot(2,3,((cnt_eye*3)+3)),plt.imshow(roi_eye_gray2, 'gray')
                plt.title(image_name+' Image')
            
            cnt_eye = cnt_eye + 1
        if len(eyes) == 0:
            ag = push_val(0)
        
        # Decision Making
        average = avg_eyeq()
        if average > 100:
            print "Eye_X: ", average
            #player.pause()
        else:
            print "---------------------", average
            pygame.mixer.music.play()
            #if player.playing == False:
            #    print "Play music"
            #    player.queue(music)
            #    player.play()

        #time.sleep(0.5)
    cv2.imshow('frame', img)
    if(simulate_real_time == "false"):
        plt.show()
    #img.releaseImage()

if __name__ == '__main__':
    if(simulate_real_time == "true"):
        countQuit = 10
        while(True):
            #time.sleep(1)
            ret, frame = cap.read()
            if frame.any() != None:
                frame = cv2.resize(frame, (600, 350))
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                detect_and_draw(frame, gray)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                print "Frame Grabbed Problem";
                countQuit = countQuit - 1
                if countQuit <= 0:
                    break
                else:
                    continue
        cap.release()
    else:

        frame = cv2.imread('face_img.jpg')
        frame = cv2.resize(frame, (600, 350))
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detect_and_draw(frame, gray)
    cv2.destroyAllWindows()