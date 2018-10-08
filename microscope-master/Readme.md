# CameraPython
## 	This folder contains Python code to control the Raspberry Pi camera module.

## Table of contents									
### - Description of Files								
### - Running: from remote computer with a GUI			
### - Running: from remote computer with command-line	
### - Running: from Raspberry Pi						
### - BackGroundSubbThread C++ Code						
### - Installation: Raspberry Pi						
### - Installation: Remote Computer					
### - Installation: Subtraction						


## Files

- run-server.sh: A bash script which asks the user for a password and connects to the Raspberry Pi from a remote computer to start the server.

- run-client-gui.sh: A bash script which runs the client that uses a GUI.

- run-client-cmd.sh: A bash script which runs the client that uses commandline.

- cameraLibServer.py: Library which contains functions for controlling the camera module of the Raspberry Pi, as well as functions which allow the Pi to be controlled from a remote computer.

- cameraLibClient.py: Library which contains functions to remotely control the Raspberry Pi from a remote computer.

- cameraServerTest.py: A server which runs indefinitely on the Raspberry Pi, which allows control of the camera module from a remote computer.

- cameraClientTest.py: A client which connects to the Raspberry Pi cameraServerTest.py script, and remotely controls the camera module.

- cameraClientGUI.py: Similar functionality to cameraClientTest.py, but runs with a GUI instead of command-line.

- picamCommand.py: A script which runs indefinitely, and controls the camera module locally from the Raspberry Pi.

- picamTest.py: A set of test functions for the image mode of the camera module.

- pividTest.py: A set of test functions for the video mode of the camera module.

- launcher.sh: A bash script which allows the python camera module server to be launched on the Raspberry Pi at boot, or when called by run-server.sh.

- BackGroundSubbThread.cpp: C++ code for background subtraction with threading utilised in order to avoid frame drops. This code is used in cameraLibClient.py.

- BackGroundSubb_Video.cpp: Old C++ code with similar functionality to BackGroundSubbThread.cpp, but drops frames due to lack of threading.

- BackGroundSubb_Video_RPI.cpp: C++ code with identical functionality to BackGroundSubb_Video.cpp, but runs on the Raspberry Pi instead of a remote computer.


## Running: from remote computer with a GUI ##

The CameraPython code can be run from a remote computer with a GUI. First, turn on the Raspberry Pi and connect to the PiNet Wi-Fi network with the remote computer.

Once connected, run run-server.sh in a terminal, and enter "PiPhysics" when prompted with a password. Then, run run-client-gui.py.

If that doesn't work, open a terminal and enter the following commands: 
	ssh pi@192.168.1.1
	cd Documents/PhysicsSummer/CameraPython
	python cameraServerTest.py

If prompted for a password, enter "PiPhysics". Then open a new terminal, and enter the following commands:
	cd Documents/Python/Olivier/microscope-master/CameraPython
	python cameraClientGUI.py


If you were successful, a GUI window should appear after a few seconds.

The GUI has five tabs: Capture Image, Record Video, Stream Video, Image Subtraction and Help.

Each tab (other than help) has a list of camera properties on the left. Changing the properties here will pass them to the microscope, as long as they're within the accepted range. Note that if exposure time is left to 0, the value used will be the duration of one frame, based on the framerate parameter.

### Capture Image Tab

The capture image tab has three sub-tabs.

The first tab is a simple image capture.
This lets you capture a single image, with an entered filename. The accepted file types are jpg, jpeg, gif, bmp.
Like all other filenames anywhere in the GUI, there are default values if no name is given. If no extension is given, the default image type is .jpg.

The second tab is trigger mode 1.
Mode 1 uses the video port. This mode allows images to be taken in rapid succession. 
However, it is possible that the image is taken before the trigger occurs. This can be fixed by increasing the IMAGE_OFFSET parameter in the cameraLibServer.py code. Additionally, the resolution cannot exceed 1920x1080 in this mode.

The third tab is trigger mode 2.
Mode 2 uses the image port. This mode results in more consistent and higher quality images. 
However, ~500 ms is required after the capture to process and store the image. Additional images cannot be taken in this period of time.

Once the image(s) are captured, they will be downloaded into the Images folder, which must exist in the same directory server launch script.

The image tab will also display the latest image that has been captured, as well as the filename of this image. Note that .gif images can not be displayed. There are buttons to open up the image in a default image editor, delete it, or rename it.

### Record Video Tab

The image tab lets you record videos. Accepted file types are mp3, mp4, m4v. More can be added at the top of the cameraLibClient.py script easily, by adding to the IMAGE_TYPES array.

A timestamp is used as a default filename if none is given. The default file extension is m4v.

The user can enter the video duration (in seconds). Otherwise, they can leave this box blank and the video will record until the 'stop' button is pressed.

Once the camera stops recording, the video will be downloaded into the Videos folder, which must exist in the same directory as the git repository.

### Stream Video Tab

The stream tab lets you stream the microscope to VLC.

The user can enter the streaming duration (in seconds). Otherwise, they can leave this box blank and the video will record until the 'stop' button is pressed.

Pressing the start button opens VLC and starts the stream.

A stream delay of 1-5 seconds will exist due to the usage of VLC.

The stream can crash if resolution and/or fps is too high.

### Image Subtraction Tab

The user can enter the recording duration (in seconds) for the image subtraction. Otherwise, they can leave this box blank and the video will record until the 'stop' button is pressed.

If an image filename is entered into the background text box, then that image will be used as a static background which is subtracted from every video frame. This image must be the same size as the current recording size.

The image associated with the image filename must be contained within the Images folder, which must exist in the same directory as the git repository.

If no background is entered, then the each video frame will be subtracted by previous video frames.

There are also two boxes to change the threshold magnitude and threshold percentage parameters.

A delay of 1-5 seconds will exist, or longer if fps and/or resolution is high.

More information about how the image subtraction mode works can be found in the "BackGroundSubbThread C++ Code" section.

### Help Tab

The help tab has some explanations to common questions, as well as 5 buttons.

Restore parameter defaults
Restore parameter values to default ones set by the Raspberry Pi, ie the ones that are loaded when microscope is turned on.

Save current parameters
Creates a save file in the Saves folder, which must exist in the same directory as the git repository. This file will use the name set in the text box, or use a default name if the box is left empty. 
The .dab (Data Attribute Bank) file created is just a text file that stores the current parameter values. Note that only variables with numeric values (ie not filenames) are saved in these files.

Open parameter file
Opens the save files from the Saves folder, which were created using the previous button, and sets the current parameter values to the values stored in the save file.

Display parameter window
Opens a window that displays the current microscope parameters, but with appropriate units.

Close microscope
Closes microscope properly. If you close the client with this button, you only need to run a run-client script to start the camera again, otherwise you need to re-run the server as well.


## Running: from remote computer with command-line

The CameraPython code can also be run without a GUI, using command-line instead. First, turn on the Raspberry Pi and connect to the PiNet Wi-Fi network with the remote computer.

Once connected, run run-server.sh in a terminal, and enter "PiPhysics" when prompted with a password. Then, run run-client-cli.py.

If that doesn't work, open a terminal and enter the following commands: 

	ssh pi@192.168.1.1
	cd Documents/PhysicsSummer/CameraPython
	python cameraServerTest.py

If prompted for a password, enter "PiPhysics". Then open a new terminal, and enter the following commands:

	cd Documents/Python/Olivier/microscope-master/CameraPython
	python cameraClientTest.py


If you were successful, a list of commands should appear.
The commands are:

	B: Set brightness
	C: Set contrast
	F: Set framerate
	G: Set gain
	H: Help
	I: Capture an image
	N: Stream to network
	O: Stream with image subtraction
	P: Get camera settings
	Q: Quit program
	R: Set resolution
	S: Set sharpness
	T: Capture with trigger
	U: Set saturation
	V: Capture a video
	X: Set exposure time

A prompt will appear to input a command.
Each command is a single letter and not case sensitive.
Input the command and press enter.

The I command takes a single image from the camera.
This command prompts for a filename to store the image in.
The filename must end in one of the following: ".jpg", ".jpeg", ".png", ".gif", ".bmp".
The default image filename is a timestamp, and used if no filename is entered into the prompt.
The image is downloaded from the Raspberry Pi to the remote computer, and stored in a folder named "Images".
The images folder must exist in the same directory that the git repository is contained in.

The T command is a trigger mode for taking images with small latency.
There are two trigger modes.
Mode 1 uses the video port.
This mode allows images to be taken in rapid succession.
However, it is possible that the image is taken before the trigger occurs.
This can be fixed by increasing the IMAGE_OFFSET parameter in the cameraLibServer.py code.
Additionally, the resolution cannot exceed 1920x1080 in this mode.
Mode 2 uses the image port.
This mode results in more consistent and higher quality images.
However, ~500 ms is required after the capture to process and store the image.
Additional images cannot be taken in this period of time.

The V command takes a video from the camera.
The program will ask for the duration of the video in seconds.
If no duration is entered, then the video will record indefinitely, until "Ctrl+C" is pressed in the terminal.
A filename will then be prompted.
A filename containing a timestamp is used if no filename is entered.
After the recording is completed, the video is downloaded to the remote computer, and stored in a folder named "Videos".
The videos folder must exist in the same directory that the git repository is contained in.

The N command streams a camera recording from the Raspberry Pi to the remote computer in real-time.
The program will ask for the duration of the video in seconds.
If no duration is entered, then the video will record indefinitely, until "Ctrl+C" is pressed in the terminal.
VLC will open and display the video stream.

The O command streams a camera recording from the Raspberry Pi to the remote computer in real-time, and performs image subtraction on the stream using OpenCV.
The program will ask for the duration of the video in seconds.
If no duration is entered, then the video will record indefinitely, until "Ctrl+C" is pressed in the terminal.
A window displaying the camera video will open, as well as another window displaying the image subtracted video.

The B, C, F, G, R, S, U, and X commands are setter functions.
For each command, the default, minimum, and maximum values are displayed for the corresponding property.
The default value is equal to the current value of the property.
If no value is entered, then the property is set to the default value.
Note that increasing the exposure time may lower the framerate, that increaing the framerate may lower the exposure time.


## Running: From Raspberry Pi

The CameraPython code can be run directly from the Raspberry Pi.
On the Raspberry Pi, open a terminal, and run the command:

	cd Documents/PhysicsSummer/CameraPython
	python picamCommand.py

The code runs the same way as on a remote computer, but with a few differences:

- Images and Videos are stored on the Raspberry Pi as opposed to a remote computer

- The N command (network streaming) does not work

- The O command (image subtraction) runs on the Raspberry Pi as opposed to streaming on a remote computer. It runs a lot slower on the Raspberry Pi.


## BackGroundSubbThread C++ Code

The BackGroundSubbThread code is used for image subtraction.
It is called within the cameraLibClient library, and may also be called from the bash command-line.
To perform background subtraction on a video file by command-line, run the command (and remove the brackets):

	./BackGroundSubbThread -vid <Video filename> thresh_p thresh_m

Background subtraction may also be performed with a static background image by running the command  (and removing the brackets):

	./BackGroundSubbThread -vid <Video filename> thresh_p thresh_m -back <Static background image filename>

The background subtraction code utilises threading in order to avoid dropping frames.
The thread goes through every single frame in the video or stream, and adds each frame to a queue.
The main thread reads from the queue, and performs background subtraction on each frame read from the queue.
If the time taken to perform background subtraction on each frame exceeds the time taken to read each frame from the stream, then a delay will occur.
A delay will normally occur if frames are being saved, if the resolution exceeds 640x480, or the framerate exceeds 30 fps.

Each background subtraction iteration produces a foreground mask.
The foreground mask contains a black and white image, where white pixels indicate changes between frames.
If a background image is used, the difference between this background and the current video stream is found.
If no background image is used, the last x recorded stream frames are used to test for change. This number of frames can be changed by editting the value of the HISTORY variable in BackGroundSubbThread.cpp and re-compiling it with the instructions in Installation: Image subtraction.

In the foreground mask image, a pixel is white when the difference in the pixel between frames is greater than the threshold magnitude, thresh_m.

If the number of white pixels in a frame exceeds a percentage threshold, thresh_p, then that frame will be saved.

Both the frame and the foreground mask is saved.
In addition, the first 100 frames are not saved, as the stream often appears green at startup. This number can be changed similarly to the HISTORY variable.

A video is created every time the number of white pixels exceeds the threshold, and the previous frame did not exceed the threshold.
Each subsequent frame is added to the video if the number of white pixels also exceeds the threshold.
The video is closed at the first subsequent frame which doesn't meet the threshold.
The videos are stored in a folder containing the timestamp that the first video was created at.
The timestamped folder is contained in the Subtract folder, in CameraPython. You may need to create this folder.
Once all image processing is completed, each frame of each video is extracted and stored as separate images.


## Installation: Raspberry Pi

The code requires the MP4Box package to place the raw video in a container, in order to playback at the correct framerate. This can be installed by:

	sudo apt-get install gpac

Netcat is also required to send image and video files to a remote computer. This can be installed by:

	sudo apt-get install netcat

Gstreamer is required to stream video to the remote computer, in order to perform image subtraction with openCV. This can be installed by:

	sudo apt-get install gstreamer-1.0

The Raspberry Pi uses an ad-hoc wireless network to connect to a remote computer. The ad-hoc wireless network can be created by first backing-up the current wireless settings:

	sudo cp /etc/network/interfaces /etc/network/interfaces-wifi

A new file is created to store the ad-hoc wireless settings:

	sudo nano /etc/network/interfaces-adhoc

Edit the file to contain the following code:

	auto lo
	iface lo inet loopback
	iface eth0 inet dhcp

	auto wlan0
	iface wlan0 inet static
	address 192.168.1.1
	netmask 255.255.255.0
	wireless-channel 11
	wireless-essid PiNet
	wireless-mode ad-hoc

Install a package to allow an IP address to be assigned to a remote computer:

	sudo apt-get install isc-dhcp-server

Edit the dhcpd config file:

	sudo nano /etc/dhcp/dhcpd.conf

Such that the file contains the following code:

	ddns-update-style interim;
	default-lease-time 600;
	max-lease-time 7200;
	authoritative;
	log-facility local7;
	subnet 192.168.1.0 netmask 255.255.255.0 {
	  range 192.168.1.5 192.168.1.150;
	}

To enable the ad-hoc wireless network, run the command:

	sudo cp /etc/network/interfaces-adhoc /etc/network/interfaces
	sudo reboot

To enable wifi, run the command:

	sudo cp /etc/network/interfaces-wifi /etc/network/interfaces
	sudo reboot

To run the python server script, type:

	python cameraServerTest.py

Alternatively, the python server script can be setup to run at boot. This can be setup by running the command:

	sudo crontab -e

The crontab file can then be edited to contain the following line:

	@reboot sh /home/pi/Documents/PhysicsSummer/CameraPython/launcher.sh


## Installation: Remote Computer

Streaming video from the camera across the network requires vlc installed in the command-line on the remote computer. On macOS, run:

	brew install Caskroom/cask/vlc

Similarly, on Ubuntu/Mint, run:

	sudo apt-get install vlc

The remote computer can connect to the Raspberry Pi, assuming that the Raspberry Pi adhoc network is set-up correctly and enabled.
The network "PiNet" should be listed in the wifi networks of the remote computer.
Once the computer is connected to the Raspberry Pi, the computer can control the Raspberry Pi camera module by running the command:

	python cameraClientTest.py

Alternatively, the camera module can be controlled by remotely connecting to the Raspberry Pi terminal:

	ssh pi@192.168.1.1
	python picamCommand.py

However, remotely running the picamCommand script will not allow video streaming over the network, nor downloading image and video files directly to the remote computer.


## Installation: Image subtraction

The C++ code "BackGroundSubbThread.cpp" is used to perform image subtraction on a network stream using OpenCV.
The network stream requires gstreamer, which must be installed before installing OpenCV.
Gstreamer can be installed by running the command:

	sudo apt-get install gstreamer-1.0
	sudo apt-get install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav

OpenCV must be installed on the remote computer to run the C++ code.
To install OpenCV, go to http://opencv.org/downloads.html and download OpenCV 3.2 (source).
Then, ensure that the following packages are installed:

	sudo apt-get install build-essential libgtk2.0-dev libjpeg-dev libtiff4-dev libjasper-dev libopenexr-dev cmake python-dev python-numpy python-tk libtbb-dev libeigen3-dev yasm libfaac-dev libopencore-amrnb-dev libopencore-amrwb-dev libtheora-dev libvorbis-dev libxvidcore-dev libx264-dev libqt4-dev libqt4-opengl-dev sphinx-common texlive-latex-extra libv4l-dev libdc1394-22-dev libavcodec-dev libavformat-dev libswscale-dev default-jdk ant libvtk5-qt4-dev

Enter the downloaded OpenCV directory, and perform the following commands:

	mkdir build
	cd build
	cmake ..
	make
	sudo make install
	sudo ldconfig

The boost library is required for threading in the C++ code.
This can be installed through the following command:

	sudo apt-get install libboost-all-dev

If changes are made to the C++ code, the code can be compiled with the following command, from a console in the CameraPython folder:

	g++ -std=c++11 BackGroundSubbThread.cpp -o BackGroundSubbThread -I/usr/local/include/opencv2 -L/usr/local/lib -lopencv_core -lopencv_video -lopencv_highgui -lopencv_videoio -lopencv_imgcodecs -lopencv_imgproc -lboost_system -lboost_thread -lboost_filesystem
