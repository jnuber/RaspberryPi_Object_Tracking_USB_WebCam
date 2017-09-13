#!/usr/bin/python3
# python Object_Detect_Tracking_Treaded.py
# by John Nuber
# Jan 2017 
# import the necessary packages

from __future__ import print_function
from imutils.video import WebcamVideoStream
from imutils.video import FPS
import imutils
import numpy as np
import cv2
import sys
import os
import curses
from time import sleep
from subprocess import check_output

os.system('cls')
          
print("Version:2017.03.15")
print(" Python: {}.{}.{}".format(sys.version_info[0],sys.version_info[1],sys.version_info[2]) )
print("  numpy: {}".format(np.__version__))
print("OpenCV2: {}\n".format(cv2.__version__))


def auto_canny(image, sigma=0.33):    # lower % = tigher canny. 33% best for most cases.
	# compute the median of the single channel pixel intensities
	v = np.median(image)

	# apply automatic Canny edge detection using the computed median
	lower = int(max(0, (1.0 - sigma) * v))
	upper = int(min(255, (1.0 + sigma) * v))
	edged = cv2.Canny(image, lower, upper)

	# return the edged image
	return edged

def find_marker(image):
	(_, cnts, _) =cv2.findContours(image.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	if not cnts:
		return 0
	
	c = max(cnts, key = cv2.contourArea)
	return cv2.minAreaRect(c)          # compute the bounding box of the of the paper region and return it

def distance_to_camera(knownWidth, focalLength, perWidth):
	if perWidth == 0:
		return 1
	# compute and return the distance from the maker to the camera
	return (knownWidth * focalLength) / perWidth


#=========================================================================================
#=========================================================================================
# set calibration image width and distance from camera in inches

KNOWN_DISTANCE =  24     # inches
KNOWN_WIDTH    =  3      # inches

# load calabration image that contains an object that is KNOWN TO BE 2 feet
# from our camera, then find the marker in the image, and initialize
# the focal length

print("Loading Calabration Image....")
image  = cv2.imread("/home/pi/images/calibration_image.jpg")
    
print(" Calibration Image Width:", image.shape[1])
print("Calibration Image Height:", image.shape[0])

gray    = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (9, 9), 0)
edged   = auto_canny(gray)

# The following was used for troubleshooting
# cv2.imshow("Calibration Image",image)

# Marker = the number of pixels that equate to the width
marker = find_marker(edged)
focalLength = (marker[1][0] * KNOWN_DISTANCE) / KNOWN_WIDTH
print("Pixcel Width", marker[1][0])
print("Focal Length", focalLength)
inches = distance_to_camera(KNOWN_WIDTH, focalLength, marker[1][0])
print("Distance", inches)

print("\nInitalizing camera in multi-thread mode")
print("Initalizing FPS stats collector in multi-thread mode\n")
camera = WebcamVideoStream(src=0).start()
camera.start() 
sleep(2)

print("Camera Active: ",camera.grabbed)
while not camera.grabbed :
	print("Restarting Camera...")
	camera = WebcamVideoStream(src=0).start()
	sleep(5)

fps = FPS().start()
camera.start() 
getFrame = camera.read()

print(" Cam Width:", getFrame.shape[1])
print("cam Height:", getFrame.shape[0])

resizeWidth = image.shape[1]
print("Target Resize Width:", image.shape[1])

#**********************************************************************
# When the webcam frame is resized to match the calibration image
# frame size, the original object distance is also decreased by the 
# ratio/difference.  Hence a resize "offset" 
# this offset is use to divide into the distance calculated in the 
# loop. 
#********************************************************************** 
offset = ((getFrame.shape[1]/(image.shape[1] * 1.0)) * 1.5)
print("Resize Distance Offset",  int(offset))

# ======================================================================
# =   Main Loop
# ======================================================================

cv2.namedWindow('Exit Panel')

while True:
	# grab the current frame, resize to new ratio, and initialize the status text
	getFrame = camera.read()
	frame = imutils.resize(getFrame, width = resizeWidth)
	f_h = (frame.shape[0])/2
	f_w = (frame.shape[1])/2
	status = "No Targets"

	# convert the frame to grayscale, blur it, and detect edges
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	#blurred = cv2.GaussianBlur(frame, (11,11),3)
	edged   = auto_canny(gray)
	marker  = find_marker(edged)
	# cv2.imshow("Edged",edged)

	if marker:
		#Calculate distance andfind contours in the edge map
		inches = (distance_to_camera(KNOWN_WIDTH, focalLength, marker[1][0])) / int(offset)
		(_,cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,	cv2.CHAIN_APPROX_SIMPLE)

		# loop over the contours
		for c in cnts:
		# approximate the contour
			peri = cv2.arcLength(c, True)
			approx = cv2.approxPolyDP(c, 0.01 * peri, True)       # ??

		# ensure that the approximated contour is "roughly" rectangular
			if len(approx) >= 4 and len(approx) <= 6:
				# compute the bounding box of the approximated contour and
				# use the bounding box to compute the aspect ratio
				(x, y, w, h) = cv2.boundingRect(approx)
				aspectRatio = w / float(h)

				# compute the solidity of the original contour
				area = cv2.contourArea(c)
				hullArea = cv2.contourArea(cv2.convexHull(c))
				solidity = area / float(hullArea)
			
				# compute whether or not the width and height, solidity, and
				# aspect ratio of the contour falls within appropriate bounds
				keepDims = w > 25 and h > 25
				keepSolidity = solidity > 0.9
				# keepAspectRatio = aspectRatio >= 0.95 and aspectRatio <= 1.05  # is a square
				# keepAspectRatio = aspectRatio >= 0.5 and aspectRatio <= 1.5

				# ensure that the contour passes all our tests
				# if keepDims and keepSolidity and keepAspectRatio:
				if keepDims and keepSolidity:

					# draw an outline around the target and update the status text
					# cv2.drawContours(frame, [approx], -1, (0, 0, 255), 1)
					status = "Target(s) Acquired"

					# compute the center of the contour region and draw the  crosshairs
					M = cv2.moments(approx)
					(cX, cY) = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
					(startX, endX) = (int(cX - (w * 0.1)), int(cX + (w * 0.1)))
					(startY, endY) = (int(cY - (h * 0.1)), int(cY + (h * 0.1)))
					#cv2.line(frame, (startX, cY), (endX, cY), (0, 0, 255), 2)
					#cv2.line(frame, (cX, startY), (cX, endY), (0, 0, 255), 2)
					
					#cv2.putText(frame, "%.2fft" % ((inches*3)/12), (frame.shape[1] - 50, frame.shape[0] - 5), cv2.FONT_HERSHEY_SIMPLEX,.5,(000,255,000), 1)
					#cv2.putText(frame,"x:{} y:{}".format(cX-f_w , cY-f_h), (5, frame.shape[0] - 5), cv2.FONT_HERSHEY_SIMPLEX, .5,(000,255,000),1)
					
				
		# draw the status text on the frame
		#cv2.putText(frame, status, (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(0,0,255), 1)
		cpuTemp= check_output(["vcgencmd", "measure_temp"]).decode("UTF-8")
		#cv2.putText(frame, cpuTemp, (frame.shape[1] - 300, frame.shape[0] - 5), cv2.FONT_HERSHEY_SIMPLEX,.5,(000,255,000), 1)	

		# show the frame and record if a key is pressed
		# cv2.imshow("Frame", frame)
		
		fps.update()
		key = cv2.waitKey(1) & 0xFF
		
		if not status == "No Targets":
			print("{} x:{} y:{} ft:{:.2f} {} ".format(status,(cX-f_w),(cY-f_h),(inches*3)/12, cpuTemp) )
		else:
			print("{} x:  y: ft:{:.2f} {} ".format(status,-00, cpuTemp) )
		
		# if the 'q' key is pressed, stop the loop
		if (key == ord("q") or key == ord("Q") or key == chr(27)):
			break

# cleanup the camera and close any open windows
fps.stop()
camera.stop()
cv2.destroyAllWindows()

print("============================================")
print("\tElasped time: {:.2f}".format(fps.elapsed()))
print("\tApprox. FPS: {:.2f}".format(fps.fps()))
print("Camera Active: ",camera.grabbed)
camera.update()
sleep(4)
