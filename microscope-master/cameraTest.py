'''
Test for the camera module without remote connection.

Author: Damon Hutley
Date: 25th November 2016
'''

import cameraLibServer

# Initialise the camera client module
cam = cameraLibServer.cameraModuleServer()

# Set the resolution
width = 1920
height = 1080
cam.setResolution(width, height)

# Set the framerate
#rate = 30
#cam.setFrameRate(rate)

# Set the exposure time
#speed = 0#30000
#cam.setExposureTime(speed)

# Take a photo
cam.capturePhoto('image.png')

# Record a video
#duration = 4
#cam.captureStream(duration, 'video2.mp4')

# Free the camera resources
cam.closeCamera()
