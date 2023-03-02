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
motion = [None, None]
time = []
date = []
counter = 0
flag1 = 0
flag2 = 0
time_flag1 = 0
time_flag2 = 0
time_flag3 = ''

# Token and ID for Telegram
token = '5860611748:AAEWG-ZjGEtZLUpEX6cKZwpP7u3L2Kjn13c'
receiver_id = 1278690585

# Defining a dataframe for storing motion date, start & end time
df = pandas.DataFrame(columns = ["Date", "Start-Time", "End-Time"])

# Construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-a", "--min-area", type=int, default=1000, help="minimum area size")
args = vars(ap.parse_args())

# Reading from the webcam
vs = cv2.VideoCapture(0)

# Create a variable to store the averaged background frame
avg = None

# Loop over the frames of the video
while True:

    # Grab the current frame and initialize the occupied/unoccupied text
    ret, frame = vs.read()
    flag1 = 0
    text = "No Motion Detected"

    # If the frame could not be grabbed, then we have reached the end of the video
    if frame is None:
        break

    # Resize the frame
    frame = imutils.resize(frame, width=1000)
    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Blur the grayscale frame to remove noise
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if avg is None:
        avg = gray.copy().astype("float")
        continue

    # Accumulate the weighted average of the frame and the background frame
    cv2.accumulateWeighted(gray, avg, 0.1)
    # Compute the absolute difference between the current frame and the background frame
    frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg))
    thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

    # Dilate the thresholded image to fill in holes, then find contours on the thresholded image
    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    # Loop over the contours
    for c in cnts:

        # If the contour is too small, ignore it
        if cv2.contourArea(c) < args["min_area"]:
            continue
        flag1 = 1

        # Compute the bounding box for the contour, draw it on the frame, and update the text
        (x,y,w,h) = cv2.boundingRect(c)
        cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0),2)
        text = "Motion Detected"

        # Initializing Alarm
        if counter == 0:
            winsound.Beep(2000,1000)
            counter = 1

        # Sending notification using Telepot in the instance of motion
        flag2 = flag2+1
        if flag2 == 1:
            time_flag1 = datetime.now()
            time_flag2 = time_flag1.timestamp()
            time_flag3 = time_flag1.strftime("%d%m%y%H%M")
            time_flag3 = 'Motion'+str(time_flag3)+'.jpg'
            date1 = time_flag1.strftime("%d %b %Y")
            time1 = time_flag1.strftime("%I:%M %p")
            msg1 = 'Motion Detected on '+str(date1)+' around '+str(time1)+'. Check the image below.'
            cv2.imwrite(time_flag3, frame)
            bot = telepot.Bot(token)
            bot.sendMessage(receiver_id, msg1)
            bot.sendPhoto(receiver_id, photo=open(time_flag3, 'rb'))

    if (datetime.now().timestamp()-time_flag2) >= 300:
        flag2 = 0

    # Appending instances of the motion in the dataframe
    motion.append(flag1)
    motion = motion[-2:]

    if motion[-1] == 1 and motion[-2] == 0:
        time.append(datetime.now().strftime("%H:%M:%S"))
        date.append(datetime.now().date())

    if motion[-1] == 0 and motion[-2] == 1:
        time.append(datetime.now().strftime("%H:%M:%S"))
        date.append(datetime.now().date())

    if text == "No Motion Detected":
        counter = 0

    # Draw the text and timestamp on the frame
    cv2.putText(frame, "Status: {}".format(text), (10,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)
    cv2.putText(frame, datetime.now().strftime("%A %d %B %Y %I:%M:%S %p"), (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)

    # Displaying the results and the video on a feed
    cv2.imshow("Security Feed", frame)
    cv2.imshow("Threshold", thresh)
    cv2.imshow("Frame Delta", frameDelta)

    key = cv2.waitKey(1) & 0xFF

    # If the `r` key is pressed, reset the counter
    if key == ord("r"):
        counter = 0

    # If the `q` key is pressed, break from the loop
    if key == ord("q"):
        if flag1 == 1:
            time.append(datetime.now().strftime("%H:%M:%S"))
            date.append(datetime.now().date())
        break

# Appending all the instances of motion to the dataframe
for i in range(0, len(time), 2):
    df = df.append({"Date":date[i], "Start-Time":time[i], "End-Time":time[i+1]}, ignore_index = True)

# Saving the dataframe as a CSV to have a log of all the instances of motion
df.to_csv("Security_Log.csv")

# Clean up the camera and close any open windows
vs.stop() if args.get("video", None) is None else vs.release()
cv2.destroyAllWindows()