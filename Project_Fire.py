# Importing Libraries
import os
import cv2
import numpy
import pandas
import imutils
from imutils.video import VideoStream
import argparse
import time
import datetime
from datetime import datetime
import winsound
import telepot

# Defining the variables
counter = 0
flag1 = 0
flag2 = 0
time_flag1 = 0
time_flag2 = 0
time_flag3 = ''
time_flag4 = 0
fire_text = ""

# Token and ID for Telegram
token = '5860611748:AAEWG-ZjGEtZLUpEX6cKZwpP7u3L2Kjn13c'
receiver_id = 1278690585

# HAAR Cascade file for fire detection
fire_cascade = cv2.CascadeClassifier('fire_detection.xml')

# Reading from the webcam
vs = cv2.VideoCapture(0)

# Loop over the frames of the video
while True:

    # Grab the current frame and initialize the text as blank
    ret, frame = vs.read()

    if flag2 == 0:
        fire_text = ""

    # If the frame could not be grabbed, then we have reached the end of the video
    if frame is None:
        break

    # Resize the frame
    frame = imutils.resize(frame, width=1000)
    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Fire Detection using HAAR Cascade file
    fire = fire_cascade.detectMultiScale(frame, 1.2, 5)

    # Drawing bounding boxes
    for (x,y,w,h) in fire:
        cv2.rectangle(frame,(x-20,y-20),(x+w+20,y+h+20),(0,0,255),2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]
        fire_text = "Fire Detected"

        # Initializing Alarm
        if counter == 0:
            winsound.Beep(2000,1000)
            counter = 1

        # Sending notification using Telepot in the instance of fire
        flag1 = flag1+1
        if flag1 == 1:
            time_flag1 = datetime.now()
            time_flag2 = time_flag1.timestamp()
            time_flag3 = time_flag1.strftime("%d%m%y%H%M")
            time_flag3 = 'Fire'+str(time_flag3)+'.jpg'
            date1 = time_flag1.strftime("%d %b %Y")
            time1 = time_flag1.strftime("%I:%M %p")
            msg1 = 'Fire Detected on '+str(date1)+' around '+str(time1)+'. Check the image below.'
            cv2.imwrite(time_flag3, frame)
            bot = telepot.Bot(token)
            bot.sendMessage(receiver_id, msg1)
            bot.sendPhoto(receiver_id, photo=open(time_flag3, 'rb'))
        if flag2 == 0:
            time_flag4 = datetime.now().timestamp()
            flag2 = 1

    if (datetime.now().timestamp()-time_flag4) >= 10:
        flag2 = 0
        counter == 0

    if (datetime.now().timestamp()-time_flag2) >= 600:
        flag1 = 0

    # Displaying certain details on the security feed
    cv2.putText(frame, "{}".format(fire_text), (10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
    cv2.putText(frame, datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"), (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)

    # Displaying the results and the video on a feed
    cv2.imshow("Security Feed", frame)

    key = cv2.waitKey(1) & 0xFF

    # If the `r` key is pressed, reset the counter
    if key == ord("r"):
        counter = 0

    # If the `q` key is pressed, break from the loop
    if key == ord("q"):
        break

# Clean up the camera and close any open windows
vs.stop() if args.get("video", None) is None else vs.release()
cv2.destroyAllWindows()