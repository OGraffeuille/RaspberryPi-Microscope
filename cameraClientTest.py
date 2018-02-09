'''
This script tests the functionallity of the camera server module. This allows 
the camera module of the Raspberry Pi to be controlled remotely via network 
connection.

Author: Damon Hutley
Date: 22nd November 2016
'''

import cameraLibClient

# Initialise the camera module server
camCommand = cameraLibClient.cameraModuleClient()

try:
	# Print a list of commands
	camCommand.printCommands()

	# Continuously ask for commands to send to the Raspberry Pi from the terminal.
	while True:
		command = camCommand.sendCommand(0)
		
		# Exit program if quit command called
		if command == "Q":
			break
finally:
	# Close connection
	camCommand.closeServer()
