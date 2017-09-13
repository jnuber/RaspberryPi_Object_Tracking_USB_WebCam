# RaspberryPi_Object_Tracking_USB_WebCam
Implementation Overview and Considerations
#
# This object tracking solutions utilize the "Triangle Similarity" method.
# In brief, the triangle similarity takes an object (marker) with a known
# width. The object is placed at some distance from the camera. Preferably
# the same camera to be used for detection and tracking.
#
# A photo/image is taken of the object using the same camera to be used for 
# object detection. We then measure the apparent width in pixels. Using 
# this image as a fixed reference point, if the camera moves away from the
# object, the number of pixels measuring the object's width decreases. If 
# the camera moves closer to the object, the number of pixels increases. 
# One can calculate the distance with pretty good accuracy. The higher the
# quality of the reference image, the better the accuracy. These attributes
# include: good lighting, good color contrast, accurate distance, as close to
# 90% camera angle as possible. In some cases, camera calibration and 
# focal length maybe required. However I found using the piCam,pinhole or
# fish-eye distortion wasn't an issue.
#  
# Solution Approach
# This solution uses a reference or calibration image of the object to 
# track. The object/marker width is determined by the number of pixels.
# Once this has been established, the main loop does the following: 
#   - looks for an object with similar contours as the reference object
#   - if found, target identified
#   - determines target width in pixels
#   - calculates distance based on a % difference from the
#     reference/calibration image
#   - locate target center
#   - display/print target details 
#   - for Raspberry Pi, get CPU temperature as well.
#
# This version previews the target, paints the target's boarders and provides
# target data on the preview screen. This an excellent method of viewing
# and debugging the code. Also included were performance stats for the 
# various functions. If using for robotics or autonomous mode, all the 
# above can be commented/removed for maximum performance. Through testing,
# with good target LIGHTING, I was achieving 30+ FPS. (Raspberry Pi 3, 
# piCam ver2, Multitheaded Camera streaming feed, Python 3.6.)
