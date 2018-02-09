/***********************************************************************
 * 
 * Test of the Picam C++ Library.
 * 
 * Author: Damon Hutley
 * Date: 2nd December 2016
 *
***********************************************************************/

/***********************************************************************
 * Header Files
***********************************************************************/

#include <ctime>
#include <fstream>
#include <iostream>
#include <string>
#include <cstdlib>
#include <climits>
#include <raspicam/raspicam_cv.h>
//#include <raspicam/raspicam.h>
#include <raspicam/raspicam_still_cv.h>
//#include <raspicam/raspicam_still.h>
#include "Picam.h"
using namespace std;

/***********************************************************************
 * Objects
***********************************************************************/

/* Create the RaspiCam object. */
raspicam::RaspiCam_Cv Camera;
//raspicam::RaspiCam Camera;

/* Create the RaspiStill object. */
raspicam::RaspiCam_Still_Cv CameraStill;
//raspicam::RaspiCam_Still CameraStill;

Picam pi(Camera, CameraStill);

/***********************************************************************
 * Main Code
***********************************************************************/

int main() {
	char command;
	int brightness;
	int contrast;
	int saturation;
	int gain;
	int speed;
	int width;
	int height;
	int duration;
	
	//initCamera();
	pi.printCommands();
	while (1) {
		command = pi.processCommand();
		
		switch(command) {
			case 'B':
				brightness = pi.processParameters('B');
				pi.setBrightness(brightness);
				break;
				
			case 'C':
				contrast = pi.processParameters('C');
				pi.setContrast(contrast);
				break;
			
			case 'F':
				cout << "Not yet implemented" << endl;
				break;
			
			case 'G':
				gain = pi.processParameters('G');
				pi.setGain(gain);
				break;
			
			case 'H':
				pi.printCommands();
				break;
			
			case 'I':
				width = pi.processParameters('W');
				height = pi.processParameters('H');
				pi.setImageResolution(width, height);
				pi.captureImage();
				break;
				
			case 'N':
				width = pi.processParameters('w');
				height = pi.processParameters('h');
				duration = pi.processParameters('D');
				pi.networkStream(width, height, duration);
				break;
				
			case 'Q':
				break;
			
			case 'S':
				saturation = pi.processParameters('S');
				pi.setSaturation(saturation);
				break;
				
			case 'V':
				width = pi.processParameters('w');
				height = pi.processParameters('h');
				pi.setVideoResolution(width, height);
				duration = pi.processParameters('D');
				pi.captureVideo(duration);
				break;
			
			case 'X':
				speed = pi.processParameters('X');
				pi.setExposureTime(speed);
				break;

			default:
				cout << "Command not recognised" << endl;
				break;
		}

		if (command == 'Q') {
			cout << "Quitting program..." << endl;
			break;
		}

		cin.clear();
		cin.ignore(10000, '\n');
	}
}
