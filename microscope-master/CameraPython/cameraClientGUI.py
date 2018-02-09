'''
This script controls the Raspberry Pi camera module through a GUI over a network.

Author: Damon Hutley
Date: 9th February 2016
'''

import cameraLibClient

# Initialise the camera module server
camCommand = cameraLibClient.cameraModuleClient()

try:
	# Run the GUI
	camCommand.runGUI()
finally:
	# Close connection
	camCommand.closeServer()
