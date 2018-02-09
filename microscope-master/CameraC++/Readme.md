# Camera C++

This folder contains C++ code to control the Raspberry Pi camera module.

## Files

- Picam.cpp: Library which contains functions for controlling the camera module using opencv.

- Picam.h: Header file for camera module control library.

- piTest.cpp: Code to control the camera module by inputing commands.

- piTest2.cpp: Test code for functions in the Picam library.

- RPiCam.cpp: Same functionality as piTest.cpp, but uses its own functions instead of the Picam library.

## Raspberry Pi installation

This code requires openCV to be installed on the Raspberry Pi. Firstly, the following packages must be installed:

	sudo apt-get install build-essential
	sudo apt-get install cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev

OpenCV can be downloaded from here: https://sourceforge.net/projects/opencvlibrary/.
To install openCV, run:

	cd opencv-3.1.0
	mkdir release
	cd release
	cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local ..
	make
	sudo make install

The C++ code requires the raspicam library. This can be downloaded from here: https://www.uco.es/investiga/grupos/ava/node/40.
To install the raspicam library on the Raspberry Pi:

	cd raspicam-0.1.3
	mkdir build
	cd build
	cmake ..
	make
	sudo make install
	sudo ldconfig
	
To compile RPiCam.cpp:
	
	g++ RPiCam.cpp -o RPiCam -I/usr/local/include -L/opt/vc/lib -lraspicam -lraspicam_cv -lmmal -lmmal_core -lmmal_util -lopencv_core -lopencv_highgui -lopencv_videoio -lopencv_imgcodecs -std=c++0x

To compile piTest.cpp:

	g++ Picam.cpp piTest.cpp -o piTest -I/usr/local/include -L/opt/vc/lib -lraspicam -lraspicam_cv -lmmal -lmmal_core -lmmal_util -lopencv_core -lopencv_highgui -lopencv_videoio -lopencv_imgcodecs -std=c++0x

To compile piTest.cpp:

	g++ Picam.cpp piTest2.cpp -o piTest2 -I/usr/local/include -L/opt/vc/lib -lraspicam -lraspicam_cv -lmmal -lmmal_core -lmmal_util -lopencv_core -lopencv_highgui -lopencv_videoio -lopencv_imgcodecs -std=c++0x

To run these programs:

	./RPiCam
	./piTest
	./piTest2

## Current Issues

- No network functionallity implemented

- Maximum resolution is 1280x960

- Maximum framerate is 30 fps

- Still mode of the raspicam library does not work. This would enable higher resolutions for images.

- This code is no longer updated in favour of the CameraPython code.
