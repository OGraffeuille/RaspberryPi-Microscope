'''
A set of tests for the video mode of the Raspberry Pi camera module.

Author: Damon Hutley
Date: 5th December 2016
'''

import cameraLibServer

def setDefaultVideoMode(camera):
	width = 1920
	height = 1080
	framerate = 30
	xt = 0
	sharpness = 0
	contrast = 0
	brightness = 50
	saturation = 0
	gain = 0

	camera.setResolution(width, height)
	camera.setFrameRate(framerate)
	camera.setExposureTime(xt)
	camera.setSharpness(sharpness)
	camera.setContrast(contrast)
	camera.setBrightness(brightness)
	camera.setSaturation(saturation)
	camera.setGain(gain)

def testLowFramerate(camera):
	width = 1920
	height = 1080
	framerate = 30
	duration = 60
	camera.setResolution(width, height)
	camera.setFrameRate(framerate)
	camera.captureStream(duration, 'vid30fps.avi')

def testMidFramerate(camera):
	width = 1280
	height = 720
	framerate = 60
	duration = 60
	camera.setResolution(width, height)
	camera.setFrameRate(framerate)
	camera.captureStream(duration, 'vid60fps.avi')

def testHighFramerate(camera):
	width = 640
	height = 480
	framerate = 90
	duration = 60
	camera.setResolution(width, height)
	camera.setFrameRate(framerate)
	camera.captureStream(duration, 'vid90fps.avi')

# Initialise the camera client module
cam = cameraLibServer.cameraModuleServer()

# Camera video framerate tests
setDefaultVideoMode(cam)
testLowFramerate(cam)
testMidFramerate(cam)
testHighFramerate(cam)

# Free the camera resources
cam.closeCamera()
