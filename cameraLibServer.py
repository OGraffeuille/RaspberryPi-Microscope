'''
Library for the control of the Raspberry Pi camera module using picamera.

Author: Damon Hutley
Date: 21st November 2016
'''


from picamera import PiCamera
from picamera import PiVideoFrame
from multiprocessing import Process, Value
from PIL import Image
from datetime import datetime
import socket
import time
import struct
import os
import sys
import select
import subprocess
import io
import threading


BRIGHTNESS_MIN = 0
BRIGHTNESS_MAX = 100
CONTRAST_MIN = -100
CONTRAST_MAX = 100
SATURATION_MIN = -100
SATURATION_MAX = 100
SHARPNESS_MIN = -100
SHARPNESS_MAX = 100
GAIN_MIN = 0
GAIN_MAX = 1600
WIDTH_MIN = 64
WIDTH_MAX = 3280
HEIGHT_MIN = 64
HEIGHT_MAX = 2464
DURATION_MIN = 0
DURATION_MAX = float("inf")
FRAMERATE_MIN = 0
FRAMERATE_MAX = 90
EXPOSURE_MIN = 0
EXPOSURE_MAX = float("inf")
IMAGE_TYPES = ['jpeg', 'jpg', 'png', 'gif', 'bmp']
IMAGE_OFFSET = 0 # Possibly need to set to 3-4


class SplitFrames(object):
	def __init__(self, camera):
		self.camera = camera
		self.frame_num = 0
		self.output = None
		self.frameout = []
		self.fnames = []

	def write(self, buf):
		if buf.startswith(b'\xff\xd8'):
			# Start of new frame; close the old one (if any) and
			# open a new output
			if self.output:
				self.output.close()

			# Offset the frame number to account for image delay in video mode.
			if any(i <= (self.frame_num - IMAGE_OFFSET) for i in self.frameout):
				fname = "../../Images/IMG_" + datetime.utcnow().strftime('%y%m%d-%H%M%S.%f')[:-3] + ".jpg"
				self.fnames.append(fname)
				self.output = io.open(fname, 'wb')
				self.output.write(buf)
				print("Captured")
				self.frameout.pop(0)

		self.frame_num += 1


class cameraModuleServer:

	def __init__(self):
		'''
		Initialise the camera module class with picamera.
		'''

		# Create an instance of the Picamera class
		try:
			self.camera = PiCamera()
		except RuntimeError:
			print "Error occurs on camera initialisation."

		PiCamera.CAPTURE_TIMEOUT = 600
		self.camera.clock_mode = "raw"

		# Initialise network variable
		self.network = 0

		# Initialise trigger mode variables
		self.start = 0
		self.end = 0
		self.ind = 0
		self.fnames = []
		self.dates = []
		self.trigflag = 0
		self.trigcount = 0

		# Initialise trigger
		self.trigger = Value('i', 0)

	def setResolution(self, width, height):
		'''
		Set the resolution of the camera.
		'''

		# Change the resolution of the camera
		self.camera.resolution = (width, height)
	def setFrameRate(self, rate):
		'''
		Set the framerate of the camera.
		'''

		# Change the framerate of the camera
		self.camera.framerate = rate
	def setExposureTime(self, speed):
		'''
		Set the exposure time of the camera. Note that the shutter speed
		must be greater than (1/framerate). A shutter speed of zero will
		result in an automatically determined exposure time.
		'''

		# Find the maximum exposure time which is limited by the camera framerate
		if self.camera.framerate != 0:
			maxSpeed = int(1000000/self.camera.framerate)
		else:
			maxSpeed = 1000000

		if speed > maxSpeed:
			# Change the framerate to allow the set exposure time
			self.camera.framerate = int(1000000/float(speed))

		# Change the shutter speed of the camera (in microseconds)
		self.camera.shutter_speed = speed
	def setSharpness(self, sharpness):
		'''
		Set the sharpness level of the camera. Min: -100, Max: 100.
		'''

		self.camera.sharpness = sharpness
	def setContrast(self, contrast):
		'''
		Set the contrast level of the camera. Min: -100, Max: 100.
		'''

		self.camera.contrast = contrast
	def setBrightness(self, brightness):
		'''
		Set the brightness level of the camera. Min: 0, Max: 100.
		'''

		self.camera.brightness = brightness
	def setSaturation(self, saturation):
		'''
		Set the saturation level of the camera. Min: -100, Max: 100.
		'''

		self.camera.saturation = saturation
	def setGain(self, gain):
		'''
		Set the gain level of the camera. If ISO is set to zero, then the
		gain will be chosen automatically. Min: 0, Max: 1600.
		'''

		self.camera.iso = gain

	def waitProcess(self, duration):
		'''
		Threaded process to wait for the duration of a recording, and to throw errors in event of camera failing.
		'''

		self.camera.wait_recording(duration)

	def delayProcess(self, duration):
		'''
		Threaded process to wait for the duration of a recording, and to throw errors in event of camera failing.
		'''

		time.sleep(duration)

	def stopProcess(self):
		'''
		Threaded process to stop recording if there is an interrupt from a network computer.
		'''

		while True:
			msg = self.recv_msg(self.hostSock)
			if msg == "Stop":
				break

	def capturePhoto(self, fname):
		'''
		Capture a photo and store on Pi.
		'''

		# Locate the Images folder
		floc = "../../Images/" + fname

		# Warm the camera up
		self.camera.start_preview()
		time.sleep(2)

		# Capture the image
		self.camera.capture(floc, use_video_port=True)
		self.camera.stop_preview()

	def paraTrigger(self, fn):
		'''
		Trigger function executed in parallel to capture function.
		'''

		if self.network == 1:
			trig = self.recv_msg(self.hostSock)
		else:
			sys.stdin = os.fdopen(fn)
			trig = str(raw_input("Trigger (T for capture, Q for quit): ")).upper()

		if trig == "T":
			self.trigger.value = 1
		elif trig == "Q":
			self.trigger.value = 2

	def captureTriggerV1(self):
		'''
		Fast capture of a series of images given a trigger. Uses video mode instead of still mode.
		'''

		# Camera setup
		self.camera.start_preview()
		time.sleep(1)

		# Initialise the custom output
		output = SplitFrames(self.camera)

		# Initialise arrays to store frame info
		self.fnames = []
		self.trigtime = []
		self.imno = 0
		endflag = 0

		# Start recording
		self.camera.start_recording(output, format='mjpeg')

		# Start the trigger process
		self.trigger.value = 0
		fn = sys.stdin.fileno()
		pt = Process(target = self.paraTrigger, args=(fn,))
		pt.start()

		while True:
			# End condition
			if endflag == 1 and self.imno == len(output.fnames):
				pt.terminate()
				break

			# Condition for when the trigger is triggered
			if not pt.is_alive():
				# Save the frame number
				if self.trigger.value == 1:
					self.trigtime.append(self.camera.timestamp)
					self.imno += 1

				# Quit the recording
				elif self.trigger.value == 2:
					endflag = 1

				# Restart the trigger process
				pt.terminate()
				self.trigger.value = 0
				pt = Process(target = self.paraTrigger, args=(fn,))
				pt.start()

			# Determine whether the current frame was recorded when the trigger occured
			if len(self.trigtime) > 0:
				if self.camera.frame.timestamp > self.trigtime[0]:
					output.frameout.append(self.camera.frame.index)
					self.trigtime.pop(0)

		# Close the recording
		self.camera.stop_recording()
		self.camera.stop_preview()

		self.fnames = output.fnames

	def captureTriggerV2(self):
		'''
		Slower implementation of captureTrigger but more consistent. Image latency is between 10-30 ms.
		However, the time taken to encode and store the image is ~500 ms.
		'''

		# Initialise to store image info
		self.fnames = []
		self.ind = 0

		# Warm-up the camera
		self.camera.start_preview()
		time.sleep(2)

		# Start the trigger process
		self.trigger.value = 0
		fn = sys.stdin.fileno()
		pt = Process(target = self.paraTrigger, args=(fn,))
		pt.start()

		while True:
			# Condition for when the trigger is triggered
			if not pt.is_alive():
				if self.trigger.value == 1:
					# Capture an image and store in file <fname>
					fname = "../../Images/IMG_" + datetime.utcnow().strftime('%y%m%d-%H%M%S.%f')[:-3] + ".jpg"
					self.fnames.append(fname)
					self.ind += 1
					self.start = time.time()
					self.camera.capture(fname,'jpeg')
					self.end = time.time()
					print("Captured in: " + str(self.end-self.start) + " seconds")

				# Quit the loop
				elif self.trigger.value == 2:
					pt.terminate()
					break

				# Restart the trigger process
				pt.terminate()
				self.trigger.value = 0
				pt = Process(target = self.paraTrigger, args=(fn,))
				pt.start()

		# Close the camera preview
		self.camera.stop_preview()

	def captureStream(self, duration, fname):
		'''
		Capture a video and store on Pi.
		'''

		# Locate the Videos folder
		floc = "../../Videos/" + fname

		# Warm up the camera
		self.camera.start_preview()
		time.sleep(2)

		# Record the camera for length <duration>, and store in file <fname>
		self.camera.start_recording("../../Videos/input.h264")

		if self.network == 1:
			# Set up camera wait processes
			p1 = Process(target = self.waitProcess, args=(duration,))
			p2 = Process(target = self.stopProcess)

			# Multiprocessing to determine when to stop recording
			p1.start()
			p2.start()
			while p1.is_alive() and p2.is_alive():
				continue
			p1.terminate()
			p2.terminate()
		else:
			try:
				self.camera.wait_recording(duration)
			except KeyboardInterrupt:
				pass

		# Stop recording once one process has finished
		self.camera.stop_recording()
		self.camera.stop_preview()

		# Place the h264 raw video file into a container, in order to get playback at the correct framerate
		os.system("MP4Box -add ../../Videos/input.h264 " + floc + " -fps " + str(self.camera.framerate))

	def networkStreamClient(self, sock, duration):
		'''
		Stream a video through the network.
		'''

		if self.network == 1:
			# Set up camera wait processes
			p1 = Process(target = self.waitProcess, args=(duration,))
			p2 = Process(target = self.stopProcess)

			# Send framerate to client
			self.send_msg(sock, str(self.camera.framerate))

			# Create a file-like object for the connection
			connection = sock.makefile('wb')
			try:
				# Warm the camera up
				self.camera.start_preview()
				time.sleep(2)

				# Record the camera for length <duration>
				self.camera.start_recording(connection, format = 'h264')

				# Multiprocessing to determine when to stop recording
				p1.start()
				p2.start()
				while p1.is_alive() and p2.is_alive():
					continue
				p1.terminate()
				p2.terminate()

				# Stop recording once one process has finished
				self.camera.stop_recording()
				self.camera.stop_preview()
			finally:
				# Free connection resources
				connection.close()
				self.closeNetwork()
				self.initNetwork()

	def networkSubtract(self, duration):
		'''
		Stream a video through the network, and allow image subtraction with openCV on the client computer.
		'''

		if self.network == 1:

			# Set up camera wait processes
			p1 = Process(target = self.delayProcess, args=(duration,))
			p2 = Process(target = self.stopProcess)

			# Send framerate to client
			self.send_msg(self.hostSock, str(self.camera.framerate))

			# Stream from picamera and pipe into gstreamer to stream over network
			cmdstr = ['gst-launch-1.0', '-v', 'fdsrc', '!', 'h264parse', '!', 'rtph264pay', 'config-interval=1', 'pt=96', '!', 'gdppay', '!', 'tcpserversink', 'host=192.168.1.1', 'port=5000']
			pcm = subprocess.Popen(cmdstr, stdin=subprocess.PIPE)
			self.camera.start_recording(pcm.stdin, format='h264')
			# Multiprocessing to determine when to stop recording
			p1.start()
			p2.start()
			while p1.is_alive() and p2.is_alive():
				continue
			p1.terminate()
			p2.terminate()

			# Stop recording
			self.camera.stop_recording()

			# Terminate the streamer command
			pcm.terminate()

		else:
			try:
				# Stream from picamera and pipe into gstreamer to stream into opencv
				cmdstr = ['gst-launch-1.0', '-v', 'fdsrc', '!', 'h264parse', '!', 'rtph264pay', 'config-interval=1', 'pt=96', '!', 'gdppay', '!', 'tcpserversink', 'host=192.168.1.1', 'port=5000']
				pcm = subprocess.Popen(cmdstr, stdin=subprocess.PIPE)
				self.camera.start_recording(pcm.stdin, format='h264')

				# Start the opencv executable
				frate = str(self.camera.framerate)
				gstcmd = "tcpclientsrc host=192.168.1.1 port=5000 ! gdpdepay ! rtph264depay ! video/x-h264, framerate=" + frate + "/1 ! avdec_h264 ! videoconvert ! appsink"
				subline = ['./BackGroundSubb_Video_RPI', '-vid', gstcmd]
				time.sleep(0.1)
				player = subprocess.Popen(subline)

				# Wait for specified duration
				time.sleep(duration)

				# Stop recording and close resources
				self.camera.stop_recording()
				pcm.terminate()
				player.terminate()

			except KeyboardInterrupt:
				# Stop recording and close resources if Ctrl+C is pressed
				self.camera.stop_recording()
				pcm.terminate()
				player.terminate()

	def send_msg(self, sock, msg):
		'''
		Send message with a prefixed length.
		'''

		# Prefix each message with a 4-byte length (network byte order)
		msg = struct.pack('>I', len(msg)) + msg
		sock.sendall(msg)

	def recv_msg(self, sock):
		'''
		Receive a message from the network.
		'''

		# Read message length and unpack it into an integer
		raw_msglen = self.recvall(sock, 4)
		if not raw_msglen:
			return None
		msglen = struct.unpack('>I', raw_msglen)[0]

		# Read the message data
		return self.recvall(sock, msglen)

	def recvall(self, sock, n):
		'''
		Decode the message given the message length.
		'''

		# Helper function to recv n bytes or return None if EOF is hit
		data = ''
		while len(data) < n:
			packet = sock.recv(n - len(data))
			if not packet:
				return None
			data += packet

		return data

	def initNetwork(self):
		'''
		Initialise the client side network on the Raspberry Pi.
		'''

		# Initialise the socket connection
		self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.host = '192.168.1.1'
		self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.server_socket.bind((self.host, 8000))
		self.server_socket.listen(0)

		# Wait for a computer to connect
		print("Waiting for connection...")
		(self.hostSock, self.address) = self.server_socket.accept()
		print("Connection accepted")
		self.server_socket.close()
		self.network = 1

	def closeNetwork(self):
		'''
		Close the client side network on the Raspberry Pi.
		'''

		self.hostSock.close()
		self.network = 0

	def printCommands(self):
		'''
		Print a list of commands.
		'''

		print("\nList of commands: ")
		print("	B: Set brightness")
		print("	C: Set contrast")
		print("	F: Set framerate")
		print("	G: Set gain")
		print("	H: Help")
		print("	I: Capture an image")
		print("	N: Stream to network")
		print("	O: Stream with image subtraction")
		print("	P: Get camera settings")
		print("	Q: Quit program")
		print("	R: Set resolution")
		print("	S: Set sharpness")
		print("	T: Capture with trigger")
		print("	U: Set saturation")
		print("	V: Capture a video")
		print("	X: Set exposure time\n")

	def sendAll(self):

		self.send_msg(self.hostSock, str(self.camera.resolution[0]))
		self.send_msg(self.hostSock, str(WIDTH_MIN))
		self.send_msg(self.hostSock, str(WIDTH_MAX))

		self.send_msg(self.hostSock, str(self.camera.resolution[1]))
		self.send_msg(self.hostSock, str(HEIGHT_MIN))
		self.send_msg(self.hostSock, str(HEIGHT_MAX))

		self.send_msg(self.hostSock, str(self.camera.framerate))
		self.send_msg(self.hostSock, str(FRAMERATE_MIN))
		self.send_msg(self.hostSock, str(FRAMERATE_MAX))

		self.send_msg(self.hostSock, str(self.camera.shutter_speed))
		self.send_msg(self.hostSock, str(EXPOSURE_MIN))
		self.send_msg(self.hostSock, str(EXPOSURE_MAX))

		self.send_msg(self.hostSock, str(self.camera.brightness))
		self.send_msg(self.hostSock, str(BRIGHTNESS_MIN))
		self.send_msg(self.hostSock, str(BRIGHTNESS_MAX))

		self.send_msg(self.hostSock, str(self.camera.contrast))
		self.send_msg(self.hostSock, str(CONTRAST_MIN))
		self.send_msg(self.hostSock, str(CONTRAST_MAX))

		self.send_msg(self.hostSock, str(self.camera.iso))
		self.send_msg(self.hostSock, str(GAIN_MIN))
		self.send_msg(self.hostSock, str(GAIN_MAX))

		self.send_msg(self.hostSock, str(self.camera.saturation))
		self.send_msg(self.hostSock, str(SATURATION_MIN))
		self.send_msg(self.hostSock, str(SATURATION_MAX))

		self.send_msg(self.hostSock, str(self.camera.sharpness))
		self.send_msg(self.hostSock, str(SHARPNESS_MIN))
		self.send_msg(self.hostSock, str(SHARPNESS_MAX))

	def inputParameter(self, parameter):
		'''
		Wait for a parameter from either the network or the Pi terminal.
		'''

		# Find the default, minimum, and maximum values for the parameter
		if parameter == "Brightness":
			default = self.camera.brightness
			minimum = BRIGHTNESS_MIN
			maximum = BRIGHTNESS_MAX

		elif parameter == "Contrast":
			default = self.camera.contrast
			minimum = CONTRAST_MIN
			maximum = CONTRAST_MAX

		elif parameter == "Gain":
			default = self.camera.iso
			minimum = GAIN_MIN
			maximum = GAIN_MAX

		elif parameter == "Saturation":
			default = self.camera.saturation
			minimum = SATURATION_MIN
			maximum = SATURATION_MAX

		elif parameter == "Sharpness":
			default = self.camera.sharpness
			minimum = SHARPNESS_MIN
			maximum = SHARPNESS_MAX

		elif parameter == "Exposure time":
			default = self.camera.shutter_speed
			minimum = EXPOSURE_MIN
			maximum = EXPOSURE_MAX

		elif parameter == "Width":
			default = self.camera.resolution[0]
			minimum = WIDTH_MIN
			maximum = WIDTH_MAX

		elif parameter == "Height":
			default = self.camera.resolution[1]
			minimum = HEIGHT_MIN
			maximum = HEIGHT_MAX

		elif parameter == "Duration":
			default = DURATION_MAX
			minimum = DURATION_MIN
			maximum = DURATION_MAX

		elif parameter == "Framerate":
			default = self.camera.framerate
			minimum = FRAMERATE_MIN
			maximum = FRAMERATE_MAX

		else:
			default = None
			minimum = None
			maximum = None

		if self.network == 1:

			# Send default, min, and max to network computer
			self.send_msg(self.hostSock, str(default))
			self.send_msg(self.hostSock, str(minimum))
			self.send_msg(self.hostSock, str(maximum))

			# Wait for parameter input from network computer
			print("Waiting for " + parameter.lower() + "...")
			value = self.recv_msg(self.hostSock)
			print(parameter + ": " + str(value))
		else:
			# Process parameter inputs from terminal
			while True:
				value = str(raw_input(parameter + " (Default: " + str(default) + ", Min: " + str(minimum) + ", Max: " + str(maximum) + "): "))

				# Set default value if there is no input
				if value == "":
					value = default
					break
				else:
					try:
						# Condition for exceeding min/max bounds
						if int(value) < minimum:
							print("Value is less than minimum")
						elif int(value) > maximum:
							print("Value is greater than maximum")
						elif value == "inf":
							value = str(sys.maxint)
							break
						else:
							break
					except ValueError:
						# Condition for parameter inputs that are not integers
						print("Not a number")

		return value

	def inputStrParameter(self, parameter):
		'''
		Wait for a parameter from either the network or the Pi terminal.
		'''

		if self.network == 1:

			# Wait for parameter input from network computer
			print("Wating for " + parameter.lower() + "...")
			value = self.recv_msg(self.hostSock)
			print(parameter + ": " + str(value))
		else:
			# Process parameter inputs from terminal
			while True:
				value = str(raw_input(parameter + " (Default: " + default + "): "))
				# Set default value if there is no input
				if value == "":
					value = default
					break
				elif parameter == "Image filename":
					# Check image filename is of correct filetype
					fpart = value.split('.',1)

					# Check file has an extension
					if len(fpart) > 1:
						ftype = fpart[-1]
					else:
						ftype = ""

					# Continue only if file extension is correct
					if ftype in IMAGE_TYPES:
						break
					else:
						print("Image filename must have one of these extensions: " + str(IMAGE_TYPES))
				else:
					# All video extensions supported, so no need to check
					break
		return value

	def confirmCompletion(self, message):
		'''
		Print confirmation message of task completion.
		'''

		if self.network == 1:
			self.send_msg(self.hostSock, message)
		else:
			print(message)

	def printStats(self):
		'''
		Print or send image/video statistics.
		'''

		# Get the image/video properties
		resolution = str(self.camera.resolution[0]) + "x" + str(self.camera.resolution[1])
		framerate = str(self.camera.framerate)
		brightness = str(self.camera.brightness)
		contrast = str(self.camera.contrast)
		again = str(self.camera.analog_gain)
		dgain = str(self.camera.digital_gain)
		sharpness = str(self.camera.sharpness)
		saturation = str(self.camera.saturation)
		xt = str(self.camera.exposure_speed)

		if self.network == 1:
			# Send the properties to the remote computer
			self.send_msg(self.hostSock, resolution)
			self.send_msg(self.hostSock, framerate)
			self.send_msg(self.hostSock, brightness)
			self.send_msg(self.hostSock, contrast)
			self.send_msg(self.hostSock, again)
			self.send_msg(self.hostSock, dgain)
			self.send_msg(self.hostSock, sharpness)
			self.send_msg(self.hostSock, saturation)
			self.send_msg(self.hostSock, xt)
		else:
			# Convert gain fractions into decimal
			if "/" in again:
				anum, aden = again.split('/')
				again = str(float(anum)/float(aden))

			if "/" in dgain:
				dnum, dden = dgain.split('/')
				dgain = str(float(dnum)/float(dden))

			# Convert contrast, sharpness, saturation to percentage
			contrast = str((int(contrast)+100)/2)
			sharpness = str((int(sharpness)+100)/2)
			saturation = str((int(saturation)+100)/2)

			# Print the properties to the Pi terminal
			print("\nProperties: ")
			print("	Resolution: " + resolution)
			print("	Framerate: " + framerate + " fps")
			print("	Brightness: " + brightness + " %")
			print("	Contrast: " + contrast + " %")
			print("	Analog gain: " + again + " dB")
			print("	Digital gain: " + dgain + " dB")
			print("	Sharpness: " + sharpness + " %")
			print("	Saturation: " + saturation + " %")
			print("	Exposure time: " + xt + " microseconds\n")

	def sendFile(self, fname, typ):
		'''
		Send an image or video file over a network.
		'''

		# Send the image via Netcat
		if typ == "Image":
			os.system("nc -l 60000 < ../../Images/" + fname)
		elif typ == "Trigger":
			self.send_msg(self.hostSock, fname)
			os.system("nc -l 60000 < " + fname)
		elif typ == "Video":
			os.system("nc -l 60000 < ../../Videos/" + fname)

	def receiveCommand(self):
		'''
		Receive a command from the network or the Pi terminal.
		'''

		if self.network == 1:
			# Recieve data from host
			print("Waiting for command...")
			command = self.recv_msg(self.hostSock)
			print("Command received: " + command)
		else:
			# Wait for command from Pi
			command = str(raw_input("Input camera command: ")).upper()

		return command

	def performCommand(self, command):
		'''
		Control the camera remotely from a network computer, or from the
		Raspberry Pi terminal.
		'''

		if command == "A":
			self.sendAll()

		# Set brightness
		elif command == "B":
			brightness = int(float(self.inputParameter("Brightness")))
			self.setBrightness(brightness)
			self.confirmCompletion("Brightness changed")

		# Set contrast
		elif command == "C":
			contrast = int(float(self.inputParameter("Contrast")))
			self.setContrast(contrast)
			self.confirmCompletion("Contrast changed")

		# Set framerate
		elif command == "F":
			rate = float(self.inputParameter("Framerate"))
			self.setFrameRate(rate)
			self.confirmCompletion("Framerate changed")

		# Set gain
		elif command == "G":
			gain = int(float(self.inputParameter("Gain")))
			self.setGain(gain)
			self.confirmCompletion("Gain changed")

		# Help
		elif command == "H":
			self.printCommands()

		# Capture photo
		elif command == "I":
			filename = self.inputStrParameter("Image filename")
			self.confirmCompletion("Image capturing...")
			self.capturePhoto(filename)
			self.confirmCompletion("Image captured")
			self.printStats()
			if self.network == 1:
				self.sendFile(filename, "Image")

		# Network stream
		elif command == "N":
			if self.network == 1:
				duration = float(self.inputParameter("Duration"))
				self.confirmCompletion("Duration set")
				self.networkStreamClient(self.hostSock, duration)
			else:
				print("Not connected to network")

		# Network subtract stream
		elif command == "O":
			duration = float(self.inputParameter("Duration"))
			self.confirmCompletion("Duration set")
			self.networkSubtract(duration)

		# Get camera settings
		elif command == "P":
			self.printStats()

		# Quit program
		elif command == "Q":
			if self.network == 1:
				print("Closing socket...")
				self.closeNetwork()

		# Set resolution
		elif command == "R":
			width = int(float(self.inputParameter("Width")))
			self.confirmCompletion("Resolution width changed")
			height = int(float(self.inputParameter("Height")))
			self.confirmCompletion("Resolution height changed")
			self.setResolution(width, height)

		# Set sharpness
		elif command == "S":
			sharpness = int(float(self.inputParameter("Sharpness")))
			self.setSharpness(sharpness)
			self.confirmCompletion("Sharpness changed")

		# Capture with trigger
		elif command == "T":
			if self.network == 1:
				mode = self.recv_msg(self.hostSock)
			else:
				while True:
					mode = str(raw_input("Enter mode (1 or 2): "))
					if mode == "1" or mode == "2":
						break
					else:
						print("Incorrect mode")
			print("Mode: " + mode)
			if mode == "1":
				self.captureTriggerV1()
			else:
				self.captureTriggerV2()
			if self.network == 1:
				for name in self.fnames:
					print("Sending")
					self.sendFile(name, "Trigger")
				self.send_msg(self.hostSock, "Q")

		# Set saturation
		elif command == "U":
			saturation = int(float(self.inputParameter("Saturation")))
			self.setSaturation(saturation)
			self.confirmCompletion("Saturation changed")

		# Capture stream
		elif command == "V":
			duration = float(self.inputParameter("Duration"))
			self.confirmCompletion("Duration set")
			filename = self.inputStrParameter("Video filename")
			self.confirmCompletion("Recording started...")
			self.captureStream(duration, filename)
			self.confirmCompletion("Recording finished")
			self.printStats()
			if self.network == 1:
				self.sendFile(filename, "Video")

		# Change exposure time
		elif command == "X":
			xt = int(float(self.inputParameter("Exposure time")))
			self.setExposureTime(xt)
			self.confirmCompletion("Exposure time changed")

		else:
			print("Not a command")

	def closeCamera(self):
		'''
		Release the camera resources.
		'''

		# Turn off the camera
		self.camera.close()
