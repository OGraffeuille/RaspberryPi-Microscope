'''
Latency test for the camera trigger function of the picamera module.

Author: Damon Hutley
Date: 16th December 2016
'''

import cameraLibServer

# Initialise the camera module
cam = cameraLibServer.cameraModuleServer()

# Properties setup
cam.setResolution(640,480)
cam.setFrameRate(90)
cam.setExposureTime(10000)

# Enter trigger mode
cam.captureTrigger()

# Print the latency and properties
print("Latency: " + str((cam.end-cam.start)/float(cam.ind+1)) + " seconds")
cam.printStats()

# Free camera resources
cam.closeCamera()
