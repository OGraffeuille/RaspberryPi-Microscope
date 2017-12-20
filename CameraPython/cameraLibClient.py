'''
Library for the control of the Raspberry Pi camera module from a host computer
via a network connection.

Author: Damon Hutley
Date: 22nd November 2016
'''

import socket
import subprocess
import time
import struct
import os
import sys
import tempfile
import glob
from multiprocessing import Process, Value
from Tkinter import Tk, Text, BOTH, W, N, E, S, RAISED, Frame, Message, LEFT, TOP, BOTTOM, DISABLED, NORMAL, PhotoImage, StringVar, Toplevel
from ttk import Button, Style, Label, Entry, Notebook
from tkFileDialog import askopenfilename
from PIL import Image, ImageTk
from datetime import datetime

# Returns the current time in milliseconds, in a date format. Used for default file names.
current_milli_time = lambda: datetime.utcnow().strftime('%y%m%d-%H%M%S.%f')[:-3]

IMAGE_TYPES = ['jpeg', 'jpg', 'gif', 'bmp'] # png causes crashing, gif isnt supported by ImageTk at the moment due to bug
VIDEO_TYPES = ['mp3', 'mp4', 'm4v']
DEFAULT_DISP_IMG = "Resources/placeholder.bmp"
THRESH_PERCENT_DEFAULT = "5"
THRESH_PERCENT_MIN = "0"
THRESH_PERCENT_MAX = "100"
THRESH_MAGNITUDE_DEFAULT = "30"
THRESH_MAGNITUDE_MIN = "1"
THRESH_MAGNITUDE_MAX = "500"

COLOUR = True

if COLOUR:
	BLACK = "\033[30m"
	RED = "\033[31m"
	GREEN = "\033[32m"
	YELLOW = "\033[33m"
	BLUE = "\033[34m"
	MAGENTA = "\033[35m"
	CYAN = "\033[36m"
	WHITE = "\033[37m"
	YELLOWFLASH = "\033[33;5m"
	CLEAR = "\033[0m"
else:
	BLACK = "\033[0m"
	RED = "\033[0m"
	GREEN = "\033[0m"
	YELLOW = "\033[0m"
	BLUE = "\033[0m"
	MAGENTA = "\033[0m"
	CYAN = "\033[0m"
	WHITE = "\033[0m"
	YELLOWFLASH = "\033[0m"
	CLEAR = "\033[0m"

class cameraGUI(Frame):

	def __init__(self, parent, camera):
		# Initialise the GUI to control the Raspberry Pi camera
		Frame.__init__(self, parent)

		self.parent = parent # root
		self.camera = camera

		self.initVars()

		self.initSVs()

		self.initUI()

	def initVars(self):
		'''
		Setting up global variables on initialisation of GUI.
		'''

		self.renameWindow = None		# Used to store image renaming window object
		self.statsWindow = None			# Used to store stats displaying window object
		self.buttonWidth = 10
		self.entryWidth = 22

		self.error = 0
		self.dispImgName = DEFAULT_DISP_IMG
		self.dispImgWidth = 348
		self.dispImgHeight = 240

		self.triggerMode = "1"			# Either 1 or 2 depending on which trigger is used by GUI
		self.trigger = StringVar()		# Used to send triggers (T or Q) to microscope

	def initSVs(self):
		'''
		Setting up the array of string variables that will store our
		microscope parameter values.

		LETTER	SV[]	COMMAND
		R		0		Width
		R		1		Height
		F		2		Framerate (fps)
		X		3		Exposure time (microseconds)
		B		4		Brightness
		C		5		Contrast
		G		6		Gain
		U		7		Saturation
		S		8		Sharpness
		O		9		Threshold percentage
		O		10		Threshold magnitude
		V		11		Video duration
		N		12		Stream duration
		O		13		Subtraction duration
		I		14		Image filename
		V		15		Video filename
		O		16		Background image
		-		17		Save filename

		There are two sets of string variables used by the GUI:
		- The entryStringVars|entrySVs are the stringvars used in Entries in the
		GUI, which then update the paramSVs
		- The paramStringVars|paramSVs are the stringvars used to store the
		actual values used by the microscope, for brightness, recording time,
		etc
		- For example, entrySVs["Brightness"] is the brightness parameter
		entered by the user. When this value is changed, sendCmd("B") is called,
		which checks that this new value is appropriate; if it is then
		paramSVs["Brightness"] will be changed to match the entrySVs[] value.
		- Not that not all paramSVs are used, namely filename ones, and the
		the entrySVs[] is used instead.
		'''

		# Saving the default parameter values
		self.camera.sendCommand("A")
		self.originalStats = self.camera.receiveAll()

		# Setting up entryStringVars[]
		self.entryStringVars = []
		for i in range(18):
			self.entryStringVars.append(StringVar())

		for i in range(0, 9):
			self.entryStringVars[i].set(self.originalStats[3*i])
		self.entryStringVars[9].set(THRESH_PERCENT_DEFAULT)
		self.entryStringVars[10].set(THRESH_MAGNITUDE_DEFAULT)
		self.entryStringVars[11].set("0")
		self.entryStringVars[12].set("0")
		self.entryStringVars[13].set("0")
		self.entryStringVars[14].set("IMG_" + current_milli_time())
		self.entryStringVars[15].set("VID_" + current_milli_time())
		self.entryStringVars[16].set("")
		self.entryStringVars[17].set("")

		# Tracing some Entry stringvars so they call sendCmd when changed
		self.entryStringVars[0].trace("w", lambda name, index, mode, _=self.entryStringVars[0]: self.sendCmd("R"))
		self.entryStringVars[1].trace("w", lambda name, index, mode, _=self.entryStringVars[1]: self.sendCmd("R"))
		self.entryStringVars[2].trace("w", lambda name, index, mode, _=self.entryStringVars[2]: self.sendCmd("F"))
		self.entryStringVars[3].trace("w", lambda name, index, mode, _=self.entryStringVars[3]: self.sendCmd("X"))
		self.entryStringVars[4].trace("w", lambda name, index, mode, _=self.entryStringVars[4]: self.sendCmd("B"))
		self.entryStringVars[5].trace("w", lambda name, index, mode, _=self.entryStringVars[5]: self.sendCmd("C"))
		self.entryStringVars[6].trace("w", lambda name, index, mode, _=self.entryStringVars[6]: self.sendCmd("G"))
		self.entryStringVars[7].trace("w", lambda name, index, mode, _=self.entryStringVars[7]: self.sendCmd("U"))
		self.entryStringVars[8].trace("w", lambda name, index, mode, _=self.entryStringVars[8]: self.sendCmd("S"))
		self.entryStringVars[9].trace("w", lambda name, index, mode, _=self.entryStringVars[9]: self.updateThresholdParam("Threshold percentage"))
		self.entryStringVars[10].trace("w", lambda name, index, mode, _=self.entryStringVars[10]: self.updateThresholdParam("Threshold magnitude"))

		# Setting up entrySVs, a python dictionary of entryStringVars[] for convenience
		self.entrySVs = {"Width":self.entryStringVars[0],	"Height":self.entryStringVars[1],
			"Framerate (fps)":self.entryStringVars[2],		"Exposure time (microseconds)":self.entryStringVars[3],
			"Brightness":self.entryStringVars[4],			"Contrast":self.entryStringVars[5],
			"Gain":self.entryStringVars[6], 				"Saturation":self.entryStringVars[7],
			"Sharpness":self.entryStringVars[8], 			"Threshold percentage":self.entryStringVars[9],
			"Threshold magnitude":self.entryStringVars[10],	"Video duration":self.entryStringVars[11],
			"Stream duration":self.entryStringVars[12],		"Subtraction duration":self.entryStringVars[13],
			"Image filename":self.entryStringVars[14],		"Video filename":self.entryStringVars[15],
			"Background image":self.entryStringVars[16],	"Save filename":self.entryStringVars[17]}

		# Setting up paramStringVars[]
		self.paramStringVars = []
		for i in range(18):
			self.paramStringVars.append(StringVar())
			self.paramStringVars[i].set(self.entryStringVars[i].get())

		# Setting up paramSVs, a python dictionary of paramStringVars[] for convenience
		self.paramSVs = {"Width":self.paramStringVars[0],	"Height":self.paramStringVars[1],
			"Framerate (fps)":self.paramStringVars[2],		"Exposure time (microseconds)":self.paramStringVars[3],
			"Brightness":self.paramStringVars[4],			"Contrast":self.paramStringVars[5],
			"Gain":self.paramStringVars[6], 				"Saturation":self.paramStringVars[7],
			"Sharpness":self.paramStringVars[8], 			"Threshold percentage":self.paramStringVars[9],
			"Threshold magnitude":self.paramStringVars[10],	"Video duration":self.paramStringVars[11],
			"Stream duration":self.paramStringVars[12],		"Subtraction duration":self.paramStringVars[13],
			"Image filename":self.paramStringVars[14],		"Video filename":self.paramStringVars[15],
			"Background image":self.paramStringVars[16],	"Save filename":self.entryStringVars[17]}

	def initUI(self):
		'''
		Completely setup and display the camera GUI.
		'''

		# Initialise the UI
		self.parent.title("Raspberry Pi Camera")
		self.style = Style()
		self.style.theme_use("clam")

		# ***** Creating notebook with tabs *****
		self.notebook = Notebook(self)

		self.imgtab = Frame(self.notebook)
		self.vidtab = Frame(self.notebook)
		self.vlctab = Frame(self.notebook)
		self.bgstab = Frame(self.notebook)
		self.hlptab = Frame(self.notebook)

		self.iconImg = PhotoImage(file=r"Resources/icon_photo_small.gif")
		self.iconVid = PhotoImage(file=r"Resources/icon_video_small.gif")
		self.iconVLC = PhotoImage(file=r"Resources/icon_vlc_small.gif")
		self.iconPen = PhotoImage(file=r"Resources/icon_pen_small.gif")

		self.notebook.add(self.imgtab, text='Capture Image', image=self.iconImg, compound="left")
		self.notebook.add(self.vidtab, text='Record Video', image=self.iconVid, compound="left")
		self.notebook.add(self.vlctab, text='Stream Video', image=self.iconVLC, compound="left")
		self.notebook.add(self.bgstab, text='Image Subtraction', image=self.iconPen, compound="left")
		self.notebook.add(self.hlptab, text='Help', compound="right")
		self.notebook.pack()

		self.pack(fill=BOTH, expand=1)


		# ***** Image tab *****

		self.imgframe1 = Frame(self.imgtab, relief=RAISED, borderwidth=1)
		self.imgnote = Notebook(self.imgtab)
		self.imgframe3 = Frame(self.imgtab, relief=RAISED, borderwidth=1)

		self.imgframe1.grid(sticky=N+E+S+W, row=0, column=0, padx=1, pady=1, rowspan=2)
		self.imgnote.grid(sticky=N+E+S+W, row=0, column=1, padx=1, pady=1)
		self.imgframe3.grid(sticky=N+E+S+W, row=1, column=1, padx=1, pady=1)
		self.imgtab.grid_columnconfigure(1, weight=1)
		self.imgtab.grid_rowconfigure(1, weight=1)

		self.dispProperties(self.imgframe1, False)

		# Notebook to switch between tabs for different image capture modes
		self.imgtabreg = Frame(self.imgnote)
		self.imgtabt1 = Frame(self.imgnote)
		self.imgtabt2 = Frame(self.imgnote)

		self.imgnote.add(self.imgtabreg, text='Image Capture')
		self.imgnote.add(self.imgtabt1, text='Trigger V1')
		self.imgnote.add(self.imgtabt2, text='Trigger V2')

		self.imgtabt1.grid_columnconfigure(1,weight=1)
		self.imgtabt1.grid_columnconfigure(2,weight=1)
		self.imgtabt1.grid_columnconfigure(3,weight=1)
		self.imgtabt2.grid_columnconfigure(1,weight=1)
		self.imgtabt2.grid_columnconfigure(2,weight=1)
		self.imgtabt2.grid_columnconfigure(3,weight=1)

		# Tab interface to do a regular image capture
		self.imglbl = Label(self.imgtabreg, text="Filename:")
		self.imglbl.grid(sticky=W, row=1, column=1, pady=4, padx=4)
		self.imgtxt = Entry(self.imgtabreg, width=self.entryWidth, textvariable=self.entryStringVars[14])
		self.imgtxt.grid(sticky=W, row=1, column=2, pady=4, padx=4)
		self.imgbut = Button(self.imgtabreg, text="Capture", width=6, command=lambda: self.sendCmd("I"))
		self.imgbut.grid(row=1, column=3, pady=4, padx=4)

		# Tab interface to capture with trigger V1
		self.imglbl2 = Label(self.imgtabt1, text="Trigger mode 1:")
		self.imglbl2.grid(sticky=W, row=1, column=0, pady=4, padx=4)
		self.imgbut2 = Button(self.imgtabt1, text="Start", width=6, command=lambda: self.sendCmd("T1"))
		self.imgbut2.grid(row=1, column=1, pady=4, padx=4)
		self.imgbut3 = Button(self.imgtabt1, text="Capture", width=6, state=DISABLED, command=lambda: self.trigger.set("T"))
		self.imgbut3.grid(row=1, column=2, pady=4, padx=4)
		self.imgbut4 = Button(self.imgtabt1, text="Stop", width=6, state=DISABLED, command=lambda: self.trigger.set("Q"))
		self.imgbut4.grid(row=1, column=3, pady=4, padx=4)

		# Tab interface to capture with trigger V2
		self.imglbl2 = Label(self.imgtabt2, text="Trigger mode 2:")
		self.imglbl2.grid(sticky=W, row=1, column=0, pady=4, padx=4)
		self.imgbut5 = Button(self.imgtabt2, text="Start", width=6, command=lambda: self.sendCmd("T2"))
		self.imgbut5.grid(row=1, column=1, pady=4, padx=4)
		self.imgbut6 = Button(self.imgtabt2, text="Capture", width=6, state=DISABLED, command=lambda: self.trigger.set("T"))
		self.imgbut6.grid(row=1, column=2, pady=4, padx=4)
		self.imgbut7 = Button(self.imgtabt2, text="Stop", width=6, state=DISABLED, command=lambda: self.trigger.set("Q"))
		self.imgbut7.grid(row=1, column=3, pady=4, padx=4)

		# Display image features
		self.imglblimg = Label(self.imgframe3)
		self.imglblimg.grid(row=0, column=0)
		self.imglblfn = Label(self.imgframe3, font=('None', 8, 'italic'), foreground="#606060")
		self.imglblfn.grid(row=1, column=0, pady=(0,2))
		self.updateDisplayImage()

		self.imgframe3.grid_columnconfigure(0,weight=1)
		self.imgframe3.grid_rowconfigure(1,weight=1)

		self.imgframe31 = Frame(self.imgframe3)
		self.imgframe31.grid(sticky=W+S+E, row=2, column=0)

		self.imgframe31.grid_columnconfigure(0,weight=1)
		self.imgframe31.grid_columnconfigure(1,weight=1)
		self.imgframe31.grid_columnconfigure(2,weight=1)

		self.imgbut8 = Button(self.imgframe31, text="Open Image", width=self.buttonWidth, command=lambda: self.openDisplayImage())
		self.imgbut8.grid(row=1, column=0, padx=4, pady=4)

		self.imgbut9 = Button(self.imgframe31, text="Rename Image", width=12.5, command=lambda: self.openRenameImageWindow())
		self.imgbut9.grid(row=1, column=1, padx=4, pady=4)

		self.imgbut10 = Button(self.imgframe31, text="Delete Image", width=self.buttonWidth, command=lambda: self.deleteDisplayImage())
		self.imgbut10.grid(row=1, column=2, padx=4, pady=4)


		# ***** Video tab *****

		self.vidframe1 = Frame(self.vidtab, relief=RAISED, borderwidth=1)
		self.vidframe2 = Frame(self.vidtab, relief=RAISED, borderwidth=1)
		self.vidframe3 = Frame(self.vidtab, relief=RAISED, borderwidth=1)

		self.vidframe1.grid(sticky=N+E+S+W, row=0, column=0, padx=1, pady=1, rowspan=2)
		self.vidframe2.grid(sticky=N+E+S+W, row=0, column=1, padx=1, pady=1)
		self.vidframe3.grid(sticky=N+E+S+W, row=1, column=1, padx=1, pady=1)
		self.vidtab.grid_columnconfigure(1, weight=1)
		self.vidtab.grid_rowconfigure(1, weight=1)


		self.dispProperties(self.vidframe1, True)

		self.vidlbl3 = Label(self.vidframe2, text="Video Recording Tab", font=(None, 12))
		self.vidlbl3.grid(row=0, column=1, pady=6, columnspan=2)

		self.vidlbl = Label(self.vidframe2, text="Enter Filename:")
		self.vidlbl.grid(sticky=W, row=1, column=1, pady=10, padx=5)

		self.vidtxt = Entry(self.vidframe2, width=self.entryWidth, textvariable=self.entryStringVars[15])
		self.vidtxt.grid(sticky=W, row=1, column=2, pady=(4,1), padx=5)

		self.vidlbl2 = Label(self.vidframe2, text="Enter Duration (s):")
		self.vidlbl2.grid(sticky=W, row=2, column=1, pady=(10, 9), padx=5)

		self.vidtxt2 = Entry(self.vidframe2, width=self.entryWidth, textvariable=self.entryStringVars[11])
		self.vidtxt2.grid(sticky=W, row=2, column=2, pady=(4,1), padx=5)

		self.vidtxt3 = Label(self.vidframe2, text="Duration of 0 will make microscope record until you stop it.", font=(None,8))
		self.vidtxt3.grid(sticky=W, row=3, column=1, pady=(0,4), padx=5, columnspan=2)

		self.vidframe21 = Frame(self.vidframe2)
		self.vidframe21.grid(sticky=W+E, row=4, column=1, columnspan=2)

		self.vidframe21.grid_columnconfigure(0,weight=1)
		self.vidframe21.grid_columnconfigure(1,weight=1)

		self.vidbut = Button(self.vidframe21, text="Start", width=10, command=lambda: self.sendCmd("V"))
		self.vidbut.grid(row=0, column=0, pady=4, padx=4)

		self.vidbut2 = Button(self.vidframe21, text="Stop", state=DISABLED, width=10, command=lambda: self.streamStop("V"))
		self.vidbut2.grid(row=0, column=1, pady=4, padx=4)


		# ***** VLC streaming tab *****

		self.vlcframe1 = Frame(self.vlctab, relief=RAISED, borderwidth=1, width=500, height=480)
		self.vlcframe2 = Frame(self.vlctab, relief=RAISED, borderwidth=1, width=500, height=480)

		self.vlcframe1.grid(sticky=N+E+S+W, row=0, column=0, padx=1, pady=1, rowspan=2)
		self.vlcframe2.grid(sticky=N+E+S+W, row=0, column=1, padx=1, pady=1)
		self.vlctab.grid_columnconfigure(1, weight=1)
		self.vlctab.grid_rowconfigure(1, weight=1)


		self.dispProperties(self.vlcframe1, True)

		self.vlclbl2 = Label(self.vlcframe2, text="Video Streaming Tab", font=(None, 12))
		self.vlclbl2.grid(row=0, column=1, pady=6, columnspan=2)

		self.vlclbl = Label(self.vlcframe2, text="Enter Duration (s):")
		self.vlclbl.grid(sticky=W, row=1, column=1, pady=10, padx=5)

		self.vlctxt2 = Entry(self.vlcframe2, width=self.entryWidth, textvariable = self.entryStringVars[12])
		self.vlctxt2.grid(sticky=W, row=1, column=2, pady=4, padx=5)

		self.vlctxt3 = Label(self.vlcframe2, text="Duration of 0 will make microscope record until you stop it.", font=(None,8))
		self.vlctxt3.grid(sticky=W, row=3, column=1, pady=(0,4), padx=5, columnspan=2)

		self.vlcframe21 = Frame(self.vlcframe2)
		self.vlcframe21.grid(sticky=W+E, row=4, column=1, columnspan=2)

		self.vlcframe21.grid_columnconfigure(0,weight=1)
		self.vlcframe21.grid_columnconfigure(1,weight=1)

		self.vlcbut = Button(self.vlcframe21, text="Start", width=10, command=lambda: self.sendCmd("N"))
		self.vlcbut.grid(row=0, column=0, pady=4, padx=4)

		self.vlcbut2 = Button(self.vlcframe21, text="Stop", state=DISABLED, width=10, command=lambda: self.streamStop("N"))
		self.vlcbut2.grid(row=0, column=1, pady=4, padx=4)


		# ***** Background subtraction tab *****

		self.bgsframe1 = Frame(self.bgstab, relief=RAISED, borderwidth=1)
		self.bgsframe2 = Frame(self.bgstab, relief=RAISED, borderwidth=1)
		self.bgsframe3 = Frame(self.bgstab, relief=RAISED, borderwidth=1)

		self.bgsframe1.grid(sticky=N+E+S+W, row=0, column=0, padx=1, pady=1, rowspan=2)
		self.bgsframe2.grid(sticky=N+E+S+W, row=0, column=1, padx=1, pady=1)
		self.bgsframe3.grid(sticky=N+E+S+W, row=1, column=1, padx=1, pady=1)
		self.bgstab.grid_columnconfigure(1, weight=1)
		self.bgstab.grid_rowconfigure(1, weight=1)

		self.dispProperties(self.bgsframe1, True)

		self.bgslbl = Label(self.bgsframe2, text="Background Subtraction Tab", font=(None, 12))
		self.bgslbl.grid(row=0, column=1, pady=6, columnspan=2)

		self.bgslbl1 = Label(self.bgsframe2, text="Enter Background Image:")
		self.bgslbl1.grid(sticky=W, row=1, column=1, pady=(10, 0), padx=5)

		self.bgsbut3 = Button(self.bgsframe2, text="Browse...", width=10, command=lambda: self.entrySVs["Background image"].set(askopenfilename().split("/")[-1]))
		self.bgsbut3.grid(sticky=W, row=2, column=2, pady=(0, 4), padx=5)

		self.bgstxt = Entry(self.bgsframe2, width=27, textvariable=self.entryStringVars[16])
		self.bgstxt.grid(sticky=W, row=2, column=1, pady=(0, 4), padx=5)

		self.bgslbl3 = Label(self.bgsframe2, text="Enter Duration (s):")
		self.bgslbl3.grid(sticky=W, row=3, column=1, pady=(10, 0), padx=5)

		self.bgstxt2 = Entry(self.bgsframe2, width=self.entryWidth, textvariable=self.entryStringVars[13])
		self.bgstxt2.grid(sticky=W, row=4, column=1, pady=(0, 4), padx=5)

		self.bgstxt3 = Label(self.bgsframe2, text="Setting duration to 0 will make microscope record forever.", font=(None,8))
		self.bgstxt3.grid(sticky=W, row=5, column=1, pady=(0,4), padx=5, columnspan=2)

		self.bgstxt4 = Label(self.bgsframe2, text="The background image must be in the Images folder.", font=(None,8))
		self.bgstxt4.grid(sticky=W, row=6, column=1, pady=(0,4), padx=5, columnspan=2)

		self.bgstxt5 = Label(self.bgsframe2, text="If no image is chosen, variations between frames is found.", font=(None,8))
		self.bgstxt5.grid(sticky=W, row=7, column=1, pady=(0,4), padx=5, columnspan=2)


		self.bgsframe3.grid_columnconfigure(1, weight=1)
		self.bgsframe31 = Frame(self.bgsframe3)
		self.bgsframe31.grid(row=8, column=1, columnspan=2, pady=8)
		self.bgsframe31.grid_columnconfigure(6, weight=1)

		self.bgslbl = Label(self.bgsframe31, text="Threshold percentage:", font=("None",10))
		self.bgslbl.grid(row=0, column=0, pady=(6,3), padx=2, sticky=W)
		self.bgslbl = Label(self.bgsframe31, textvariable=self.paramStringVars[9], font=("None",10), width=5)
		self.bgslbl.grid(row=0, column=1, pady=(6,3), padx=(2,0), sticky=W)
		self.bgstxt = Entry(self.bgsframe31, width=4, textvariable=self.entryStringVars[9])
		self.bgstxt.grid(row=0, column=2, pady=(6,3), padx=(0,12))
		self.bgstxt.bind("<FocusOut>", self.updateSVs)
		self.bgslbl = Label(self.bgsframe31, text=THRESH_PERCENT_MIN, font=("None",9))
		self.bgslbl.grid(row=0, column=3, pady=(6,3), padx=3, sticky=E)
		self.bgslbl = Label(self.bgsframe31, text="-", font=("None",9))
		self.bgslbl.grid(row=0, column=4, pady=(6,3), padx=3)
		self.bgslbl = Label(self.bgsframe31, text=THRESH_PERCENT_MAX, font=("None",9))
		self.bgslbl.grid(row=0, column=5, pady=(6,3), padx=3, sticky=W)

		self.bgslbl = Label(self.bgsframe31, text="What percentage of pixels need to change to record a frame.", font=("None",8))
		self.bgslbl.grid(row=1, column=0, pady=(0,4), padx=2, sticky=W, columnspan=8)

		self.bgslbl = Label(self.bgsframe31, text="Threshold magnitude:", font=("None",10))
		self.bgslbl.grid(row=2, column=0, pady=(6,3), padx=2, sticky=W)
		self.bgslbl = Label(self.bgsframe31, textvariable=self.paramStringVars[10], font=("None",10), width=5)
		self.bgslbl.grid(row=2, column=1, pady=(6,3), padx=(2,0), sticky=W)
		self.bgstxt = Entry(self.bgsframe31, width=4, textvariable=self.entryStringVars[10])
		self.bgstxt.grid(row=2, column=2, pady=(6,3), padx=(0,12))
		self.bgstxt.bind("<FocusOut>", self.updateSVs)
		self.bgslbl = Label(self.bgsframe31, text=THRESH_MAGNITUDE_MIN, font=("None",9))
		self.bgslbl.grid(row=2, column=3, pady=(6,3), padx=3, sticky=E)
		self.bgslbl = Label(self.bgsframe31, text="-", font=("None",9))
		self.bgslbl.grid(row=2, column=4, pady=(6,3), padx=3)
		self.bgslbl = Label(self.bgsframe31, text=THRESH_MAGNITUDE_MAX, font=("None",9))
		self.bgslbl.grid(row=2, column=5, pady=(6,3), padx=3, sticky=W)

		self.bgslbl = Label(self.bgsframe31, text="Amount of change required for a pixel to have 'changed'.", font=("None",8))
		self.bgslbl.grid(row=3, column=0, pady=(0,4), padx=2, sticky=W, columnspan=8)

		self.bgsframe22 = Frame(self.bgsframe3)
		self.bgsframe22.grid(sticky=W+E, row=9, column=1, columnspan=2)

		self.bgsframe22.grid_columnconfigure(0,weight=1)
		self.bgsframe22.grid_columnconfigure(1,weight=1)

		self.bgsbut = Button(self.bgsframe22, text="Start", width=10, command=lambda: self.sendCmd("O"))
		self.bgsbut.grid(row=0, column=0, pady=4, padx=4)

		self.bgsbut2 = Button(self.bgsframe22, text="Stop", state=DISABLED, width=10, command=lambda: self.streamStop("O"))
		self.bgsbut2.grid(row=0, column=1, pady=4, padx=4)


		# ***** Help program tab *****

		self.hlpframe1 = Frame(self.hlptab, relief=RAISED, borderwidth=1)
		self.hlpframe2 = Frame(self.hlptab, relief=RAISED, borderwidth=1)

		self.hlpframe1.grid(sticky=N+E+S+W, row=0, column=0, padx=1, pady=1)
		self.hlpframe2.grid(sticky=N+E+S+W, row=0, column=1, padx=1, pady=1)
		self.hlptab.grid_rowconfigure(0, weight=1)
		self.hlptab.grid_columnconfigure(1, weight=1)

		self.hlplbl6 = Label(self.hlpframe1, text="Additional Tools", font=(None, 12))
		self.hlplbl6.grid(row=0, column=1, padx=6, pady=10, columnspan=2)

		self.hlplbl = Label(self.hlpframe1, text="Restore parameter defaults")
		self.hlplbl.grid(sticky=E, row=1, column=1, padx=6, pady=10)
		self.hlpbut = Button(self.hlpframe1, text="Restore", width=8, command=lambda: self.resetParams())
		self.hlpbut.grid(row=1, column=2, padx=6, pady=10)

		self.hlplbl2 = Label(self.hlpframe1, text="Save current parameters")
		self.hlplbl2.grid(sticky=E, row=2, column=1, padx=6, pady=(6,0))
		self.hlpbut2 = Button(self.hlpframe1, text="Save", width=8, command=lambda: self.saveStatsFile())
		self.hlpbut2.grid(row=2, column=2, padx=6, rowspan=2)
		self.hlptxt = Entry(self.hlpframe1, width=19, textvariable=self.entryStringVars[17])
		self.hlptxt.grid(sticky=E, row=3, column=1, padx=6, pady=(0,6))

		self.hlplbl3 = Label(self.hlpframe1, text="Open parameter file")
		self.hlplbl3.grid(sticky=E, row=4, column=1, padx=6, pady=10)
		self.hlpbut3 = Button(self.hlpframe1, text="Open", width=8, command=lambda: self.readStatsFile())
		self.hlpbut3.grid(row=4, column=2, padx=6, pady=10)

		self.hlplbl4 = Label(self.hlpframe1, text="Display parameter window")
		self.hlplbl4.grid(sticky=E, row=5, column=1, padx=6, pady=10)
		self.hlpbut4 = Button(self.hlpframe1, text="Display", width=8, command=lambda: self.openStatsWindow())
		self.hlpbut4.grid(row=5, column=2, padx=6, pady=10)

		self.hlpframe1.grid_rowconfigure(6, weight=1)
		self.hlpbut5 = Button(self.hlpframe1, text="Close Microscope", width=20, command=lambda: self.camera.quitGUI(self))
		self.hlpbut5.grid(sticky=S, row=6, column=1, columnspan=2, padx=20, pady=20)


		self.hlplbl6 = Label(self.hlpframe2, text="Information", font=(None, 12))
		self.hlplbl6.grid(row=0, column=1, padx=6, pady=10)

		descriptions = (
		"Accepted image file extensions are: " + ", ".join(IMAGE_TYPES) + ". "
		"\nImages with .gif extension can not be displayed in GUI tab."
		"\nAccepted video file extensions are: " + ", ".join(VIDEO_TYPES) + "."
		"\n\nIf you set exposure time to 0, a default value will be based on framerate."
		"\n\nThere are two trigger modes:"
		"\nMode 1 uses the video port. This mode allows images to be taken in rapid succession. However, it is possible that the image is taken before the trigger occurs. This can be fixed by increasing the IMAGE_OFFSET parameter in the cameraLibServer code. Additionally, the resolution cannot exceed 1920x1080 in this mode."
		"\nMode 2 uses the image port. This mode results in more consistent and higher quality images. However, ~500 ms is required after the capture to process and store the image. Additional images cannot be taken in this period of time."
		)
		self.hlpmsg = Message(self.hlpframe2, text=descriptions)
		self.hlpmsg.grid(row=1, column=1)

	def dispProperties(self, frame, isVideoTab):
		'''
		Creates the UI that displays and lets the user change the generic
		parameter values. If isVideoTab is true, then exposure rate will be
		greyed out, otherwise fps will be greyed out.
		'''

		# Receive the camera properties from the Raspberry Pi
		stats = self.originalStats

		# Determine column values
		ncolumn = 0 	# Property names
		pcolumn = 1		# Property values
		ecolumn = 2		# Entry boxes
		mincolumn = 3	# Min property values
		scolumn = 4		# '-' seperator
		maxcolumn = 5	# Max property values

		# Setting up titles
		self.titlbl1 = Label(frame, text="Properties", font=("None", 11))
		self.titlbl1.grid(row=0, column=ncolumn, columnspan=ecolumn, pady=(8,9), padx=3)

		self.titlbl2 = Label(frame, text="Value", font=("None", 11))
		self.titlbl2.grid(row=0, column=ecolumn, columnspan = 1, pady=(8,9), padx=3)

		self.titlbl3 = Label(frame, text="Range", font=("None", 11))
		self.titlbl3.grid(row=0, column=mincolumn, columnspan = 3, pady=(8,9), padx=3)

		propnames = ["Width (pixels):",
					"Height (pixels):",
					"Framerate (fps):",
					u"Exp. Time (\u03bcs):",
					"Brightness:",
			  		"Contrast:",
			  		"ISO:",
			  		"Saturation:",
			  		"Sharpness:"]

		# Adding entries, and labels showing property name, value, min, -, max
		for i in range(0,9):
			lbl = Label(frame, text=propnames[i], font=("None",10))
			lbl.grid(row=i+1, column=ncolumn, pady=8, padx=2, sticky=E)

			lbl2 = Label(frame, textvariable=self.paramStringVars[i], font=("None",10), width=5)
			lbl2.grid(row=i+1, column=pcolumn, pady=8, padx=(2,0), sticky=W)

			txt = Entry(frame, width=4, textvariable=self.entryStringVars[i])
			txt.grid(row=i+1, column=ecolumn, pady=8, padx=(0,12))
			txt.bind("<FocusOut>", self.updateSVs)

			lbl3 = Label(frame, text=stats[3*i+1], font=("None",9))
			lbl3.grid(row=i+1, column=mincolumn, pady=8, padx=3, sticky=E)

			lbl4 = Label(frame, text="-", font=("None",9))
			lbl4.grid(row=i+1, column=scolumn, pady=8, padx=3)

			lbl5 = Label(frame, text=stats[3*i+2], font=("None",9))
			lbl5.grid(row=i+1, column=maxcolumn, pady=8, padx=3, sticky=W)

	def updateSVs(self, event):
		'''
		Determine if the values in the GUI entries match the paramater values,
		and change them if they don't. Sometimes if entries are changed too
		quickly, the params don't change in time.
		'''

		for i in range(11):
			if self.entryStringVars[i].get() != self.paramStringVars[i].get():
				self.entryStringVars[i].set(self.paramStringVars[i].get())

	def sendCmd(self, useCmd):
		'''
		Start running the given command, and disable some UI if we're videoing.
		'''

		# Don't send image subtraction command if background image size doesn't
		# match current recording size, or doesn't exist
		if useCmd == "O" and self.entrySVs["Background image"].get() != "":
			try:
				img = Image.open("Images/" + self.entrySVs["Background image"].get())
			except IOError:
				print(RED + "ERROR: Can't open background image." + CLEAR)
				return
			w1 = self.paramSVs["Width"].get()
			h1 = self.paramSVs["Height"].get()
			w2 = img.size[0]
			h2 = img.size[1]
			if int(w1) != int(w2) or int(h1) != int(h2):
				print(RED + "ERROR: Sizes don't match." + CLEAR)
				print(RED + "Current recording dimensions are: " + str(w1) + "x" + str(h1) + "." + CLEAR)
				print(RED + "Selected background image is of dimensions: " + str(w2) + "x" + str(h2) + "." + CLEAR)
				return

		# For commands that take time to complete, the GUI buttons and entries
		# are disabled, so that only the stop button can be pressed
		if useCmd == "T1" or useCmd == "T2" or useCmd == "V" or useCmd == "N" or useCmd == "O":

			self.disableWidgets(self.parent, useCmd)

			if useCmd == "T1":
				useCmd = "T"
				self.triggerMode = "1"
			elif useCmd == "T2":
				useCmd = "T"
				self.triggerMode = "2"

			# Perform the specified command, give it time to let GUI update
			self.parent.after(10, self.camera.sendCommand, useCmd)
		else:
			# Send command without delay
			self.camera.sendCommand(useCmd)

	def updateThresholdParam(self, cmd):
		'''
		Function that updates the threshold values if they're changed in entries.
		This isn't done through sendCmd like the other parameters because the
		threshold parameters are only client sided and don't need to send a
		command to the server.
		'''

		try:
			val = self.entrySVs[cmd].get()
			if val == "":
				val = "0"
			if float(val) < 0:
				val = "0"
			if cmd == "Threshold percentage":
				if float(val) >= float(THRESH_PERCENT_MIN) and float(val) <= float(THRESH_PERCENT_MAX):
					self.paramSVs[cmd].set(val)
			elif cmd == "Threshold magnitude":
				if float(val) >= float(THRESH_MAGNITUDE_MIN) and float(val) <= float(THRESH_MAGNITUDE_MAX):
					self.paramSVs[cmd].set(val)
		except:
			pass

	def streamStop(self, useCmd):
		'''
		Process that is run if the stop button is pressed.
		If no command is specified then this just reactivates disabled UI.
		'''

		# Re-enable all the buttons after the stop button has been pressed
		self.disableWidgets(self.parent, "Enable")

		# Set the value to stop the stream/record process
		self.camera.procStop.value = 1
		time.sleep(1)

		if useCmd == "V":
			# Receive the video file
			self.camera.printStats()
			self.camera.receiveFile(self.camera.videoName, "Video")

		elif useCmd == "N":
			# Free connection resources
			print(GREEN + "Network stream closed" + CLEAR)
			self.camera.client_socket.close()
			self.camera.client_socket = socket.socket()
			self.camera.client_socket.connect(('192.168.1.1', 8000))

	def disableWidgets(self, parent, useCmd):
		'''
		Enables or disables all entries and buttons (other than stop buttons)
		that are children of parent. Works recursively. useCmd is what command
		is being activated, or "Enable" to re-enable widgets.
		'''

		# Disable (or enable) all widgets in parent, and parent's children
		for w in parent.winfo_children():
			if w.winfo_class() == "TEntry" or w.winfo_class() == "TButton":
				if useCmd == "Enable":
					w.config(state=NORMAL)
				else:
					w.config(state=DISABLED)
			else:
				self.disableWidgets(w, useCmd)

		# After all children widgets have been iterated through and activated,
		# the stop buttons are disactivated (or vise versa)
		if parent == self.parent:
			if useCmd == "Enable":
				self.imgbut3.config(state=DISABLED)
				self.imgbut4.config(state=DISABLED)
				self.imgbut6.config(state=DISABLED)
				self.imgbut7.config(state=DISABLED)
				self.vidbut2.config(state=DISABLED)
				self.vlcbut2.config(state=DISABLED)
				self.bgsbut2.config(state=DISABLED)
			elif useCmd == "T1":
				self.imgbut3.config(state=NORMAL)
				self.imgbut4.config(state=NORMAL)
			elif useCmd == "T2":
				self.imgbut6.config(state=NORMAL)
				self.imgbut7.config(state=NORMAL)
			elif useCmd == "V":
				self.vidbut2.config(state=NORMAL)
			elif useCmd == "N":
				self.vlcbut2.config(state=NORMAL)
			elif useCmd == "O":
				self.bgsbut2.config(state=NORMAL)

	def updateDisplayImage(self):
		'''
		Updates the image being displayed in the image tab to the latest image
		taken by the microscope, or a placeholder otherwise.
		'''

		# Deciding on what image we should be displaying.
		# Priority: most recent non-gif photo in Image folder > default image
		imageList = []
		for type in IMAGE_TYPES:
			imageList.extend(glob.glob("Images/*." + type))

		if len(imageList) > 0:
			imageList = sorted(imageList, key=os.path.getctime)
			while True:
				img = imageList.pop()
				if (img[-3:]) != "gif":
					self.dispImgName = "Images/" + img.split("/")[-1]
					break
				if len(imageList) == 0:
					print(RED + ".gif images can not be displayed." + CLEAR)
					self.dispImgName = DEFAULT_DISP_IMG
					break
		else:
			self.dispImgName = DEFAULT_DISP_IMG

		# Updating the display image and name of image imgtab
		image = Image.open(self.dispImgName)
		scale = min(float(self.dispImgWidth)/image.size[0], float(self.dispImgHeight)/image.size[1])
		image = image.resize((int(image.size[0]*scale), int(image.size[1]*scale)), Image.ANTIALIAS)

		self.dispImg = ImageTk.PhotoImage(image)
		self.imglblimg.configure(image=self.dispImg)
		self.imglblfn.configure(text=self.dispImgName)

	def deleteDisplayImage(self):
		'''
		Deletes the last image taken by the microscope, ie the one currently
		being displayed in the image tab.
		'''

		if (self.dispImgName == DEFAULT_DISP_IMG):
			print(RED + "Can't delete default display image." + CLEAR)
		else:
			try:
				os.remove(self.dispImgName)
				self.updateDisplayImage()
			except OSError:
				print(RED + "Couldn't delete display image." + CLEAR)

	def openDisplayImage(self):
		'''
		Opens the display image in a default photo viewer.
		'''

		try:
			image = Image.open(self.dispImgName)
			image.show()
		except OSError:
		    pass

	def openRenameImageWindow(self):
		'''
		Opens a window that lets you manually edit the filename of the display image.
		'''
		if self.dispImgName == DEFAULT_DISP_IMG:
			print(RED + "Can't change default image name." + CLEAR)

		elif (self.renameWindow == None) or (self.renameWindow.winfo_exists() == 0):
			self.renameWindow = Toplevel(self)
			self.renameWindow.wm_title("Edit Image Filename")

			fname = StringVar()
			fname.set(self.dispImgName.split("/")[-1])

			ext = ""
			parts = self.dispImgName.split(".")
			if (len(parts) > 1) and (parts[-1] in IMAGE_TYPES):
				ext = "." + parts[-1]

			lbl = Label(self.renameWindow, text="Editting name of " + self.dispImgName)
			lbl.grid(sticky=W, row=0, column=0, padx=6, pady=6, columnspan=3)

			lbl2 = Label(self.renameWindow, text="New filename:")
			lbl2.grid(sticky=W, row=1, column=0, padx=6, pady=(6,15))

			txt = Entry(self.renameWindow, textvariable=fname, width=25)
			txt.grid(row=1, column=1, padx=6, pady=(6,15), columnspan=2)

			but = Button(self.renameWindow, text="Default", command= lambda: fname.set("IMG_" + current_milli_time() + ext))
			but.grid(row=2, column=0, padx=2, pady=2)

			but = Button(self.renameWindow, text="Cancel", command= self.renameWindow.destroy)
			but.grid(row=2, column=1, padx=2, pady=2)

			but = Button(self.renameWindow, text="Save", command= lambda: self.renameImage(fname.get()))
			but.grid(row=2, column=2, padx=2, pady=2)

			self.renameWindow.geometry("%dx%d+%d+%d" % (350, 111, self.parent.winfo_x() + 500, self.parent.winfo_y()))
		else:
			self.renameWindow.focus_set()

	def renameImage(self, fname):
		'''
		Function called when the "save" button is pressed in the renameImage window.
		Changes file name of the display image, updates UI, and closes window.
		'''

		newfn = "/".join(self.dispImgName.split("/")[0:-1]) + "/" + fname
		os.rename(self.dispImgName, newfn)
		self.dispImgName = newfn
		self.imglblfn.configure(text=self.dispImgName)
		self.renameWindow.destroy()

	def resetParams(self):
		'''
		Make the server store its default parameters, and return these one at a
		time to reset parameter values.
		'''

		for i in range(0, 9):
			if self.entryStringVars[i].get() != self.originalStats[3*i]:
				self.entryStringVars[i].set(self.originalStats[3*i])

	def openStatsWindow(self):
		'''
		Creates a window that shows the current camera parameters, with units.
		'''

		# Create window if it doesn't already exist
		if (self.statsWindow == None) or (self.statsWindow.winfo_exists() == 0):
			self.statsWindow = Toplevel(self)
			self.statsWindow.wm_title("Camera Parameter Statistics")
		else:
			self.statsWindow.focus_set()

		# Get the camera to update its properties
		self.sendCmd("P")

		stats = ["Resolution: " + str(self.camera.resolution),
				"Framerate: " + str(self.camera.framerate) + " fps",
				"Brightness: " + str(self.camera.brightness) + " %",
				"Contrast: " + str(self.camera.contrast) + " %",
				"Analog gain: " + str(float(self.camera.again)) + " dB",
				"Digital gain: " + str(float(self.camera.dgain)) + " dB",
				"Sharpness: " + str(self.camera.sharpness) + " %",
				"Saturation: " + str(self.camera.saturation) + " %",
				"Exposure time: " + str(self.camera.xt) + " microseconds"]

		lbl = Label(self.statsWindow, text="Camera Parameters", font=(None, 12))
		lbl.grid(sticky=W, row=0, column=0, padx=6, pady=6, columnspan=3)

		for i in range(0,9):
			lbl = Label(self.statsWindow, text=stats[i])
			lbl.grid(sticky=W, row=i+1, column=0, padx=6, pady=6, columnspan=3)

		self.statsWindow.geometry("%dx%d+%d+%d" % (250, 325, self.parent.winfo_x() + 500, self.parent.winfo_y()))

	def saveStatsFile(self):
		'''
		Creates a save of the current microscope parameters.
		'''

		filename = self.entrySVs["Save filename"].get()
		if filename == "":
			filename = "SAV_" + current_milli_time()

		try:
			fid = open("Saves/" + filename + ".dab", "w")

			for var in self.paramSVs:
				val = str(self.paramSVs[var].get())
				if sum((c.isalpha() or c.isspace()) for c in val) == 0 and val != "":
					fid.write(var + " " + str(self.paramSVs[var].get()) + "\n")

			fid.close()

		except IOError:
			pass

	def readStatsFile(self):
		'''
		Opens a stats file selected by user, and updates the microscope's
		parameters to that of the save file.
		'''

		try:
			fid = open(askopenfilename(), "r")

			for ln in fid:
				val = ln.split(" ")[-1][:-1]
				var = ln[0:-len(val)-2]

				if self.entrySVs[var].get() != val:
					self.entrySVs[var].set(val)

			fid.close()

		except IOError:
			print("Error reading stats file: Tried to open invalid file.")


class cameraModuleClient:

	def __init__(self):
		'''
		Initialise the server to the Raspberry Pi.
		'''

		# Initialise the socket connection

		self.client_socket = socket.socket()
		print(YELLOW + "Waiting for connection..." + CLEAR)
		self.client_socket.connect(('192.168.1.1', 8000))
		print(GREEN + "Connection accepted" + CLEAR)

		# GUI settings
		self.useGUI = 0
		self.procStop = Value('i', 0)
		self.videoName = ""
		self.confStop = ""
		self.msgSent = 0

		# Camera properties (given in units converted by printStats())
		self.resolution = 0
		self.framerate = 0
		self.brightness = 0
		self.contrast = 0
		self.again = 0
		self.dgain = 0
		self.sharpness = 0
		self.saturation = 0
		self.xt = 0

	def networkStreamServer(self, duration):
		'''
		Recieve a video stream from the Pi, and playback through VLC.
		'''

		# Determine the framerate of the stream
		frate = self.recv_msg(self.client_socket)
		self.msgSent = 0

		# Make a file-like object for the connection
		connection = self.client_socket.makefile('rb')

		try:
			# Start stream to VLC
			cmdline = ['vlc', '--demux', 'h264', '--h264-fps', frate, '-']
			player = subprocess.Popen(cmdline, stdin=subprocess.PIPE)
			while True:
				# Send data to VLC input
				data = connection.read(1024)
				if not data:
					break
				player.stdin.write(data)

				# Finish if stop button is pressed
				if self.useGUI == 1 and self.procStop.value == 1 and self.app.paramSVs["Stream duration"].get() == str(sys.maxint):
					raise KeyboardInterrupt

		except (KeyboardInterrupt, IOError):
			self.send_msg(self.client_socket, "Stop")
			self.msgSent = 1
			time.sleep(1)

		# Close resources
		connection.close()
		player.terminate()

		if not self.useGUI == 1 or not self.app.paramSVs["Stream duration"].get() == str(sys.maxint):
			# Free connection resources
			print(GREEN + "Network stream closed" + CLEAR)
			self.client_socket.close()
			self.client_socket = socket.socket()
			self.client_socket.connect(('192.168.1.1', 8000))

	def networkStreamSubtract(self, duration):
		'''
		Recieve a video stream from the Pi, and perform image subtraction through openCV.
		'''

		# Determine the framerate of the stream
		frate = self.recv_msg(self.client_socket)

		try:
			if self.useGUI == 1:
				thresh_p = self.app.paramSVs["Threshold percentage"].get()
				thresh_m = self.app.paramSVs["Threshold magnitude"].get()
			else:
				thresh_p = THRESH_PERCENT_DEFAULT
				thresh_m = THRESH_MAGNITUDE_DEFAULT

			# Receive a stream from gstreamer, and pipe into the openCV executable.
			gstcmd = "tcpclientsrc host=192.168.1.1 port=5000 ! gdpdepay ! rtph264depay ! video/x-h264, framerate=" + frate + "/1 ! avdec_h264 ! videoconvert ! queue max-size-buffers=0 max-size-time=0 max-size-bytes=0 ! appsink"

			# Determine whether a static image is used as the background
			if self.useGUI == 0 or (self.useGUI == 1 and self.app.entrySVs["Background image"].get() == ""):
				subline = ['./BackGroundSubbThread', '-vid', gstcmd, thresh_p, thresh_m]
			else:
				subline = ['./BackGroundSubbThread', '-vid', gstcmd, thresh_p, thresh_m, '-back', os.getcwd() + '/Images/' + self.app.entrySVs["Background image"].get()]

			# Initiate the background subtraction process
			time.sleep(0.1)
			player = subprocess.Popen(subline, preexec_fn=os.setpgrp)

			if self.useGUI == 1 and self.app.paramSVs["Subtraction duration"].get() == str(sys.maxint):
				# Stop when stop button is pressed or process has ended
				while player.poll() == None:
					if self.procStop.value == 1:
						raise KeyboardInterrupt
			else:
				# Wait for executable to exit
				player.wait()

		except KeyboardInterrupt:
			# Tell the Raspberry Pi to stop the process
			self.send_msg(self.client_socket, "Stop")
			player.wait()

	def returnThreshold(self):
		'''
		Returns the threshold parameter for image subtraction (what /% of the
		frame needs to have changed to save the image). This function is called
		in BackGroundSubbThread.cpp.
		'''

		if self.useGUI == 1:
			return 6.
		else:
			return 5.

	def nextFilename(self, filename, param):
		'''
		Creates the default filename for the next file to be saved in GUI.
		param = "Image filename", "Video filename"
		'''

		if self.useGUI == 1:
			fn = filename

			# Finding extension of filename
			parts = fn.split(".")
			if (len(parts) > 1) and ((parts[-1] in IMAGE_TYPES) or (parts[-1] in VIDEO_TYPES)):
				ext = "." + parts[-1]
				fn = fn[0:-len(ext)]
			else:
				ext = ""

			if ((fn[0:4] == "IMG_") or (fn[0:4] == "VID_")) and (sum(c.isdigit() for c in fn[4:22]) == 15) and fn[10] == "-" and fn[17] == ".":
				# Re-generating filename if user is using default one
				newfn = fn[0:4] + current_milli_time() + ext
			else:
				# Incremenent filename if user is using custom one
				parts = fn.split("-")
				if (len(parts[-1]) != sum(c.isdigit() for c in parts[-1])):
					newfn = fn + "-2" + ext
				else:
					parts[-1] = str(int(parts[-1]) + 1)
					newfn = "-".join(parts) + ext

			self.app.entrySVs[param].set(newfn)

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

	def printCommands(self):
		'''
		Print a list of commands.
		'''

		print("\nList of commands: ")
		print("B: Set brightness")
		print("C: Set contrast")
		print("F: Set framerate")
		print("G: Set gain")
		print("H: Help")
		print("I: Capture an image")
		print("N: Stream to network")
		print("O: Stream with image subtraction")
		print("P: Get camera settings")
		print("Q: Quit program")
		print("R: Set resolution")
		print("S: Set sharpness")
		print("T: Capture with trigger")
		print("U: Set saturation")
		print("V: Capture a video")
		print("X: Set exposure time\n")

	def receiveAll(self):
		'''
		Receive all camera properties for use by the GUI.
		'''

		result = []

		# Fetch all camera properties, including mins and maxs
		for i in range(27):
			result.append(self.recv_msg(self.client_socket))

		return result

	def processIntParameter(self, param):
		'''
		Wait for parameter from the terminal, and then send integer to the Pi.
		'''

		# Receive default, min, max parameters from Pi
		default = self.recv_msg(self.client_socket)
		minimum = self.recv_msg(self.client_socket)
		maximum = self.recv_msg(self.client_socket)

		# Convert default fractions into decimal
		if "/" in default:
			num, den = default.split('/')
			default = str(float(num)/float(den))

		# Input parameter value from terminal or GUI
		while True:
			if self.useGUI == 1:
				value = self.app.entrySVs[param].get()
			else:
				value = str(raw_input(param + " (Default: " + str(default) + ", Min: " + str(minimum) + ", Max: " + str(maximum) + "): "))

			if value == "":
				value = "0"
			if value <= "0" and "duration" in param:
				value = str(sys.maxint)
			try:
				# Condition for exceeding min/max bounds
				if float(value) < float(minimum):
					if self.useGUI == 1:
						value = default
						self.app.error = 1
						break
					else:
						print(RED + "Value is less than minimum" + CLEAR)
				elif float(value) > float(maximum):
					if self.useGUI == 1:
						value = default
						self.app.error = 1
						break
					else:
						print(RED + "Value is greater than maximum" + CLEAR)
				elif value == "inf":
					value = str(sys.maxint)
					break
				else:
					break
			except ValueError:
				# Condition for parameter inputs that are not integers
				if self.useGUI == 1:
					value = default
					self.app.error = 1
					break
				else:
					print(RED + "Not a number" + CLEAR)

		# Send parameter value to Pi
		self.send_msg(self.client_socket, value)

		# Receive confirmation message from the Pi.
		confirm = self.recv_msg(self.client_socket)
		if confirm == None:
			raise Exception("Command Failed (May need to lower resolution or framerate)")
		else:
			if self.useGUI == 1 and self.app.error == 0:
				if "Resolution" in confirm:
					confirm = "Resolution changed"
			elif self.useGUI == 1 and self.app.error == 1:
				self.app.error = 0
			else:
				print(GREEN + confirm + CLEAR)

		if self.useGUI == 1:
			self.app.paramSVs[param].set(value)

		return value

	def processStrParameter(self, param):
		'''
		Decides on an appropriate string parameter (file name) and send it to Pi.
		'''

		if (param == "Image filename"):
			default = "IMG_" + current_milli_time()
		elif (param == "Video filename"):
			default = "VID_" + current_milli_time()

		# Input parameter value from terminal or GUI
		if self.useGUI == 1:
			value = self.app.entrySVs[param].get()
		else:
			value = str(raw_input(param + " (Default: " + str(default) + "): "))

		# Set default value if there is no input
		if value == "":
			value = default

		# Check file has an extension
		fpart = value.split('.')
		if len(fpart) > 1:
			ftype = fpart[-1]
		else:
			ftype = ""

		# Add extension if there is no appropriate extension currently
		if (param == "Image filename"):
			if ftype not in IMAGE_TYPES:
				value += ".jpg"
		elif (param == "Video filename"):
			if ftype in VIDEO_TYPES:
				value += ".m4v"

		# Send parameter value to Pi
		self.send_msg(self.client_socket, value)

		# Receive start confirmation message from the Pi.
		confirm = self.recv_msg(self.client_socket)
		if confirm == None:
			raise Exception("Command Failed (May need to lower resolution or framerate)")
		else:
			if self.useGUI != 1:
				print(YELLOW + confirm + CLEAR)

		try:
			# Receive finish confirmation message from the Pi.
			confirm = self.recv_msg(self.client_socket)
		except KeyboardInterrupt:
			# Send message to stop recording if Ctrl+C is pressed
			self.send_msg(self.client_socket, "Stop")
			confirm = self.recv_msg(self.client_socket)

		if confirm == None:
			raise Exception("Command Failed (May need to lower resolution or framerate)")
		else:
			if self.useGUI != 1:
				print(GREEN + confirm + CLEAR)

		return value

	def filenameGUI(self, param):
		'''
		Get the video filename if the GUI is used. In order to use the stop
		button correctly, this has to be in a separate function
		to processStrParameter.
		'''

		if (param == "Image filename"):
			default = "IMG_" + current_milli_time()
		elif (param == "Video filename"):
			default = "VID_" + current_milli_time()

		# Input parameter value from terminal or GUI
		if self.useGUI == 1:
			value = self.app.entrySVs[param].get()
		else:
			value = str(raw_input(param + " (Default: " + str(default) + "): "))

		# Set default value if there is no input
		if value == "":
			value = default

		# Check file has an extension
		fpart = value.split('.')
		if len(fpart) > 1:
			ftype = fpart[-1]
		else:
			ftype = ""

		# Add extension if there is no appropriate extension currently
		if (param == "Video filename"):
			if ftype in VIDEO_TYPES:
				value += ".m4v"

		# Send parameter value to Pi
		self.send_msg(self.client_socket, value)

		# Receive start confirmation message from the Pi.
		confirm = self.recv_msg(self.client_socket)
		if confirm == None:
			raise Exception("Command Failed (May need to lower resolution or framerate)")
		else:
			if self.useGUI != 1:
				print(YELLOW + confirm + CLEAR)

		return value


	def videoGUI(self):
		'''
		If the duration is infinite, then determine whether the stop
		button of the GUI has been pressed.
		'''

		while True:
			# Stop the process by setting the value
			if self.procStop.value == 1:
				break
		# Send message to stop recording if Ctrl+C is pressed
		self.send_msg(self.client_socket, "Stop")
		self.confStop = self.recv_msg(self.client_socket)

	def printStats(self):
		'''
		Receive and print image/video stats after capture.
		'''

		# Receive properties of the image/video from the Raspberry Pi
		self.resolution = self.recv_msg(self.client_socket)
		self.framerate = self.recv_msg(self.client_socket)
		self.brightness = self.recv_msg(self.client_socket)
		self.contrast = self.recv_msg(self.client_socket)
		self.again = self.recv_msg(self.client_socket)
		self.dgain = self.recv_msg(self.client_socket)
		self.sharpness = self.recv_msg(self.client_socket)
		self.saturation = self.recv_msg(self.client_socket)
		self.xt = self.recv_msg(self.client_socket)

		# Convert gain fractions into decimal
		if "/" in self.again:
			anum, aden = self.again.split('/')
			self.again = str(float(anum)/float(aden))

		if "/" in self.dgain:
			dnum, dden = self.dgain.split('/')
			self.dgain = str(float(dnum)/float(dden))

		# Convert contrast, sharpness, saturation to percentage
		self.contrast = str((int(self.contrast)+100)/2)
		self.sharpness = str((int(self.sharpness)+100)/2)
		self.saturation = str((int(self.saturation)+100)/2)

		if self.useGUI == 0:
			print("\nProperties: ")
			print("Resolution: " + self.resolution)
			print("Framerate: " + self.framerate + " fps")
			print("Brightness: " + self.brightness + " %")
			print("Contrast: " + self.contrast + " %")
			print("Analog gain: " + str(float(self.again)) + " dB")
			print("Digital gain: " + str(float(self.dgain)) + " dB")
			print("Sharpness: " + self.sharpness + " %")
			print("Saturation: " + self.saturation + " %")
			print("Exposure time: " + self.xt + " microseconds\n")

	def receiveFile(self, fname, typ):
		'''
		Receive an image or video from the Pi.
		'''
		if self.useGUI != 1:
			print(YELLOW + "Downloading file..." + CLEAR)

		# Must have Netcat installed on the command-line
		if typ == "Image":
			time.sleep(0.1)
			filepath = os.getcwd() + "/Images/" + fname
			os.system("nc 192.168.1.1 60000 > " + filepath)

		elif typ == "Trigger":
			while True:
				# Unlike the other types, triggers recieve file name through recv_msg,
				# and fname is the entire file path rather than just the file name.
				fname = self.recv_msg(self.client_socket)
				print("Receiving...")
				if fname == "Q":
					break
				else:
					fname = fname.split("/")[-1]
					time.sleep(0.1)
					filepath = os.getcwd() + "/Images/" + fname
					os.system("nc 192.168.1.1 60000 > " + filepath)

		elif typ == "Video":
			time.sleep(0.1)
			filepath = os.getcwd() + "/Videos/" + fname
			os.system("nc 192.168.1.1 60000 > " + filepath)

		if self.useGUI != 1:
			print(GREEN + "Downloaded file" + CLEAR)

	def getTriggerMode(self):
		'''
		Identifies whether trigger mode 1 or trigger mode 2 is being used.
		'''

		if self.useGUI == 1:
			mode = self.app.triggerMode
		else:
			print(CYAN + "Note: Option 1 uses the video port, which means there is a latency of 0-300 ms," + CLEAR)
			print(CYAN + "  but allows images to be taken in rapid succession." + CLEAR)
			print(CYAN + "  Option 2 uses the still port, which has a latency of 10-30 ms," + CLEAR)
			print(CYAN + "  but requires ~500 ms after capture to process and store the image." + CLEAR)
			while True:
				mode = str(raw_input("Enter mode (1 or 2): "))
				if mode == "1" or mode == "2":
					break
				else:
					print("Incorrect mode")

		return mode

	def sendTrigger(self):
		'''
		Send triggers to immediately capture an image.
		'''

		while True:
			if self.useGUI == 1:
				# Waits until either capture or stop button have been clicked
				# When these buttons are clicked, they also update app.trigger
				self.app.imgbut.wait_variable(self.app.trigger)
				trigger = self.app.trigger.get()
			else:
				trigger = str(raw_input("Trigger (T for capture, Q for quit): ")).upper()

			self.send_msg(self.client_socket, trigger)

			# Capture trigger
			if trigger == "T":
				print("Capturing")

			# Quit trigger mode
			if trigger == "Q":
				break

	def sendCommand(self, useCmd):
		'''
		Send a command via terminal to the Raspberry Pi.
		'''

		# List of commands
		opt = ["B","C","F","G","H","I","N","O","P","Q","R","S","T","U","V","X"]

		time.sleep(0.1)

		if self.useGUI == 1:
			command = useCmd
		else:
			# Input command from terminal
			command = 0
			while command not in opt:
				command = str(raw_input("Input camera command: ")).upper()
				if command not in opt:
					print(RED + "Invalid command" + CLEAR)
				else:
					print(GREEN + "Command sent: " + command + CLEAR)

		# Send command
		self.send_msg(self.client_socket, command)

		# Send parameters and perform command
		# Set brightness
		if command == "B":
			self.processIntParameter("Brightness")

		# Set contrast
		elif command == "C":
			self.processIntParameter("Contrast")

		# Change framerate
		elif command == "F":
			self.processIntParameter("Framerate (fps)")

		# Set gain
		elif command == "G":
			if self.useGUI != 1:
				print(CYAN + "Note: Gain of 0 automatically sets the gain" + CLEAR)
			self.processIntParameter("Gain")

		# Help
		elif command == "H":
			self.printCommands()

		# Caputre photo
		elif command == "I":
			filename = self.processStrParameter("Image filename")
			self.printStats()
			self.receiveFile(filename, "Image")
			if self.useGUI == 1:
				self.nextFilename(filename, "Image filename")
				self.app.updateDisplayImage()

		# Network stream
		elif command == "N":
			duration = self.processIntParameter("Stream duration")
			if self.useGUI == 1 and self.app.paramSVs["Stream duration"].get() == str(sys.maxint):
				self.procStop.value = 0
				prc = Process(target = self.networkStreamServer, args=(duration,))
				prc.start()
			else:
				print(CYAN + "Note: Press Ctrl+C to exit recording" + CLEAR)
				self.networkStreamServer(duration)
				if self.useGUI == 1:
					self.app.disableWidgets(self.root, "Enable")

		# Network subtract stream
		elif command == "O":
			#if self.useGUI == 1 and self.isCorrectBackground(self.app.paramSVs["Background image"].get()) == True:
			duration = self.processIntParameter("Subtraction duration")
			if self.useGUI == 1 and self.app.paramSVs["Subtraction duration"].get() == str(sys.maxint):
				self.procStop.value = 0
				prc = Process(target = self.networkStreamSubtract, args=(duration,))
				prc.start()
			else:
				print(CYAN + "Note: Press Ctrl+C to exit recording" + CLEAR)
				self.networkStreamSubtract(duration)
				if self.useGUI == 1:
					self.app.disableWidgets(self.root, "Enable")
			#elif self.useGUI == 1:
			#	time.sleep(1)
			#	self.app.disableWidgets(self.root, "Enable")

		# Print camera settings
		elif command == "P":
			self.printStats()

		# Change resolution
		elif command == "R":
			self.processIntParameter("Width")
			self.processIntParameter("Height")

		# Set sharpness
		elif command == "S":
			self.processIntParameter("Sharpness")

		# Capture with trigger
		elif command == "T":
			mode = self.getTriggerMode()
			self.send_msg(self.client_socket, mode)
			self.sendTrigger()
			self.receiveFile("", "Trigger")
			if self.useGUI == 1:
				self.app.disableWidgets(self.root, "Enable")
				self.app.updateDisplayImage()

		# Set saturation
		elif command == "U":
			self.processIntParameter("Saturation")

		# Capture stream
		elif command == "V":
			self.processIntParameter("Video duration")
			if self.useGUI == 1 and self.app.paramSVs["Video duration"].get() == str(sys.maxint):
				self.videoName = self.filenameGUI("Video filename")
				self.nextFilename(self.videoName, "Video filename")
				self.procStop.value = 0
				prc = Process(target = self.videoGUI)
				prc.start()
			else:
				print(CYAN + "Note: Press Ctrl+C to exit recording" + CLEAR)
				self.videoName = self.processStrParameter("Video filename")
				self.nextFilename(self.videoName, "Video filename")
				self.printStats()
				self.receiveFile(self.videoName, "Video")
				if self.useGUI == 1:
					self.app.disableWidgets(self.root, "Enable")

		# Change exposure time
		elif command == "X":
			if self.useGUI != 1:
				print(CYAN + "Note: Exposure time of 0 automatically sets the exposure time" + CLEAR)
			self.processIntParameter("Exposure time (microseconds)")

		return command

	def runGUI(self):
		'''
		Initialise the camera GUI, and run the GUI loop.
		'''

		self.useGUI = 1
		self.root = Tk()
		self.root.geometry("675x415+150+150")
		self.app = cameraGUI(self.root, self)
		self.root.mainloop()

	def quitGUI(self, app):
		'''
		Quit the GUI, and tell the Raspberry Pi to quit also.
		'''

		app.quit()
		self.sendCommand("Q")

	def closeServer(self):
		'''
		Free server resources.
		'''

		# Close the connection and socket
		print(YELLOW + "Closing socket..." + CLEAR)
		self.client_socket.close()
