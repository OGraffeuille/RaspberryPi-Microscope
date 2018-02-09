/***********************************************************************
 * 
 * A set of test functions for the Picam C++ library.
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
 * Functions
***********************************************************************/

void testLowestRes() {
	int width;
	int height;
	
	width = 320;
	height = 240;
	pi.setImageResolution(width, height);
	pi.captureImageFname("cpp320x240.png");
}

void testLowRes() {
	int width;
	int height;
	
	width = 640;
	height = 480;
	pi.setImageResolution(width, height);
	pi.captureImageFname("cpp640x480.png");
}

void testMedRes() {
	int width;
	int height;
	
	width = 1280;
	height = 720;
	pi.setImageResolution(width, height);
	pi.captureImageFname("cpp1280x720.png");
}

void testHighRes() {
	int width;
	int height;
	
	width = 1920;
	height = 1080;
	pi.setImageResolution(width, height);
	pi.captureImageFname("cpp1920x1080.png");
}

void testHigherRes() {
	int width;
	int height;
	
	width = 2560;
	height = 1440;
	pi.setImageResolution(width, height);
	pi.captureImageFname("cpp2560x1440.png");
}

void testHighestRes() {
	int width;
	int height;
	
	width = 3280;
	height = 2464;
	pi.setImageResolution(width, height);
	pi.captureImageFname("cpp3280x2464.png");
}

/***********************************************************************
 * Main Code
***********************************************************************/

int main() {
	//testLowestRes();
	testLowRes();
	testMedRes();
	testHighRes();
	testHigherRes();
	testHighestRes();
}
