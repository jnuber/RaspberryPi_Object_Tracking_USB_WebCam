#!/usr/bin/env python3
# python  object_tracking_calibration.py

# Import the necessary packages
from __future__ import print_function
import numpy as np
import argparse
import cv2
import imutils
import sys
import os.path 
from time import sleep

print("Python:", sys.version)
print("OpenCV Version", cv2.__version__)

homeFolder = "/home/pi/images"
calibration_image = "/home/pi/images/calibration_image.jpg"
print("Path:", homeFolder)
# print("path:", os.path_isdir  )

# construct the argument parse and parse the arguments
#ap = argparse.ArgumentParser()
#ap.add_argument("-f", "--frame", required = True,
#       help = "path to the fame image")
#ap.add_argument("-g", "--goal", required = True,
#       help = "path to goal image")
#args = vars(ap.parse_args())


camera = cv2.VideoCapture(0)

print(" Video Width:" ,camera.get(cv2.CAP_PROP_FRAME_WIDTH)) 
print("Video Heigth:" ,camera.get(cv2.CAP_PROP_FRAME_HEIGHT))

status = "Target Calibration Image - Press 'q' to exit"
instructions = "Set camera exactly 24inchs or 2ft from target."
while True:
	(grabbed, frame) = camera.read()
	cv2.putText(frame, status, (10,15), cv2.FONT_HERSHEY_SIMPLEX,.375,(000,000,255), 1)
	cv2.putText(frame, instructions, (frame.shape[1]-frame.shape[1]+10, frame.shape[0] - 5), cv2.FONT_HERSHEY_SIMPLEX,.5,(000,255,000), 1)

	cv2.imshow("Target Calibration Image",frame)
	key = cv2.waitKey(1) & 0xFF
	sleep(.25)
	
	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		break

# Save calibration image -- OpenCV handles converting filetypes
(grabbed, frame) = camera.read()
resize = imutils.resize(frame,height=240)
cv2.imwrite(calibration_image, resize)
print("")
print("   *************************************************")
print("Calibration Image Saved to: {}".format(calibration_image))
camera.release()
cv2.destroyAllWindows()

quit()
