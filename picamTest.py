'''
A set of tests for the Raspberry Pi camera module using the Python camera library.

Author: Damon Hutley
Date: 2nd December 2016
'''

import cameraLibServer

def setDefaultImageMode(camera):
	width = 2560
	height = 1440
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

def testLowestRes(camera):
	width = 320
	height = 240
	camera.setResolution(width, height)
	camera.capturePhoto('im320x240.png')

def testLowRes(camera):
	width = 640
	height = 480
	camera.setResolution(width, height)
	camera.capturePhoto('im640x480.png')

def testMedRes(camera):
	width = 1280
	height = 720
	camera.setResolution(width, height)
	camera.capturePhoto('im1280x720.png')

def testHighRes(camera):
	width = 1920
	height = 1080
	camera.setResolution(width, height)
	camera.capturePhoto('im1920x1080.png')

def testHigherRes(camera):
	width = 2560
	height = 1440
	camera.setResolution(width, height)
	camera.capturePhoto('im2560x1440.png')

def testHighestRes(camera):
	'''
	Does not work.
	'''
	width = 3280
	height = 2464
	camera.setResolution(width, height)
	camera.capturePhoto('im3280x2464.png')
	
def testLowestSharpness(camera):
	sharpness = -100
	camera.setSharpness(sharpness)
	camera.capturePhoto('sharp-100.png')
	
def testLowSharpness(camera):
	sharpness = -50
	camera.setSharpness(sharpness)
	camera.capturePhoto('sharp-50.png')
	
def testMidSharpness(camera):
	sharpness = 0
	camera.setSharpness(sharpness)
	camera.capturePhoto('sharp0.png')
	
def testHighSharpness(camera):
	sharpness = 50
	camera.setSharpness(sharpness)
	camera.capturePhoto('sharp50.png')
	
def testHighestSharpness(camera):
	sharpness = 100
	camera.setSharpness(sharpness)
	camera.capturePhoto('sharp100.png')
	
def testLowestContrast(camera):
	contrast = -100
	camera.setContrast(contrast)
	camera.capturePhoto('contr-100.png')
	
def testLowContrast(camera):
	contrast = -50
	camera.setContrast(contrast)
	camera.capturePhoto('contr-50.png')
	
def testMidContrast(camera):
	contrast = 0
	camera.setContrast(contrast)
	camera.capturePhoto('contr0.png')
	
def testHighContrast(camera):
	contrast = 50
	camera.setContrast(contrast)
	camera.capturePhoto('contr50.png')
	
def testHighestContrast(camera):
	contrast = 100
	camera.setContrast(contrast)
	camera.capturePhoto('contr100.png')
	
def testLowestBrightness(camera):
	brightness = 0
	camera.setBrightness(brightness)
	camera.capturePhoto('bright0.png')
	
def testLowBrightness(camera):
	brightness = 25
	camera.setBrightness(brightness)
	camera.capturePhoto('bright25.png')
	
def testMidBrightness(camera):
	brightness = 50
	camera.setBrightness(brightness)
	camera.capturePhoto('bright50.png')
	
def testHighBrightness(camera):
	brightness = 75
	camera.setBrightness(brightness)
	camera.capturePhoto('bright75.png')
	
def testHighestBrightness(camera):
	brightness = 100
	camera.setBrightness(brightness)
	camera.capturePhoto('bright100.png')
	
def testLowestSaturation(camera):
	saturation = -100
	camera.setSaturation(saturation)
	camera.capturePhoto('satur-100.png')
	
def testLowSaturation(camera):
	saturation = -50
	camera.setSaturation(saturation)
	camera.capturePhoto('satur-50.png')
	
def testMidSaturation(camera):
	saturation = 0
	camera.setSaturation(saturation)
	camera.capturePhoto('satur0.png')
	
def testHighSaturation(camera):
	saturation = 50
	camera.setSaturation(saturation)
	camera.capturePhoto('satur50.png')
	
def testHighestSaturation(camera):
	saturation = 100
	camera.setSaturation(saturation)
	camera.capturePhoto('satur100.png')
	
def testLowestGain(camera):
	gain = 100
	camera.setGain(gain)
	camera.capturePhoto('gain100.png')
	
def testLowGain(camera):
	gain = 200
	camera.setGain(gain)
	camera.capturePhoto('gain200.png')
	
def testMidGain(camera):
	gain = 400
	camera.setGain(gain)
	camera.capturePhoto('gain400.png')
	
def testHighGain(camera):
	gain = 640
	camera.setGain(gain)
	camera.capturePhoto('gain640.png')
	
def testHighestGain(camera):
	gain = 800
	camera.setGain(gain)
	camera.capturePhoto('gain800.png')
	
def testLowestXT(camera):
	xt = 6600
	camera.setExposureTime(xt)
	camera.capturePhoto('xt6600.png')
	
def testLowXT(camera):
	xt = 13200
	camera.setExposureTime(xt)
	camera.capturePhoto('xt13200.png')
	
def testMidXT(camera):
	xt = 19800
	camera.setExposureTime(xt)
	camera.capturePhoto('xt19800.png')
	
def testHighXT(camera):
	xt = 26400
	camera.setExposureTime(xt)
	camera.capturePhoto('xt26400.png')
	
def testHighestXT(camera):
	xt = 33000
	camera.setExposureTime(xt)
	camera.capturePhoto('xt33000.png')

# Initialise the camera client module
cam = cameraLibServer.cameraModuleServer()

## Camera image resolution tests
#setDefaultImageMode(cam)
#testLowestRes(cam)
#testLowRes(cam)
#testMedRes(cam)
#testHighRes(cam)
testHigherRes(cam)
##testHighestRes(cam)

## Camera image sharpness tests
#setDefaultImageMode(cam)
#testLowestSharpness(cam)
#testLowSharpness(cam)
#testMidSharpness(cam)
#testHighSharpness(cam)
#testHighestSharpness(cam)

## Camera image contrast tests
#setDefaultImageMode(cam)
#testLowestContrast(cam)
#testLowContrast(cam)
#testMidContrast(cam)
#testHighContrast(cam)
#testHighestContrast(cam)

## Camera image brightness tests
#setDefaultImageMode(cam)
#testLowestBrightness(cam)
#testLowBrightness(cam)
#testMidBrightness(cam)
#testHighBrightness(cam)
#testHighestBrightness(cam)

## Camera image saturation tests
#setDefaultImageMode(cam)
#testLowestSaturation(cam)
#testLowSaturation(cam)
#testMidSaturation(cam)
#testHighSaturation(cam)
#testHighestSaturation(cam)

### Camera image gain tests
#setDefaultImageMode(cam)
#testLowestGain(cam)
#testLowGain(cam)
#testMidGain(cam)
#testHighGain(cam)
#testHighestGain(cam)

## Camera image exposure time tests
#setDefaultImageMode(cam)
#testLowestXT(cam)
#testLowXT(cam)
#testMidXT(cam)
#testHighXT(cam)
#testHighestXT(cam)

# Free the camera resources
cam.closeCamera()
