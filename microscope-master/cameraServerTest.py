'''
This script tests the functionallity of the camera server module. This allows 
the camera module of the Raspberry Pi to be controlled remotely via network 
connection.

Author: Damon Hutley
Date: 23rd November 2016
'''

import cameraLibServer
import picamera
from multiprocessing import Process
import time
import sys
import subprocess

# Initialise the camera module client
camCommand = cameraLibServer.cameraModuleServer()

try:
	# Continuously wait for commands from a computer on the network
	while True:
		if camCommand.network == 0:
			# Initialise the network
			camCommand.initNetwork()
		else:
			#try:
			# Process and perform command from network
			command = camCommand.receiveCommand()
			camCommand.performCommand(command)
			
			# Close network if quit command called
			if command == "Q":
				time.sleep(1)
				camCommand.closeNetwork()
					
			#except:
				## Restart the server if an error occurs
				#e = sys.exc_info()[0]
				#print("Error: %s" % e)
				#try:
					## Occasionally the camera will fail when trying to close
					#camCommand.closeCamera()
					#camCommand.__init__()
				#except:
					#print("Cannot close camera")
				#time.sleep(1)
				#camCommand.closeNetwork()
finally:	
	# Free the camera resources
	print("Closing camera...")
	camCommand.closeCamera()
