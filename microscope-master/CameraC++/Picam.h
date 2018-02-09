#ifndef PICAM_H
#define PICAM_H

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
using namespace std;

#define BRIGHTNESS_MIN 0
#define BRIGHTNESS_MAX 100
#define CONTRAST_MIN 0
#define CONTRAST_MAX 100
#define SATURATION_MIN 0
#define SATURATION_MAX 100
#define GAIN_MIN 0
#define GAIN_MAX 100
#define EXPOSURE_MIN 0
#define EXPOSURE_MAX 100
#define WIDTH_IMG_MIN 64
#define WIDTH_IMG_MAX 3280
#define WIDTH_VID_MIN 64
#define WIDTH_VID_MAX 1280
#define HEIGHT_IMG_MIN 64
#define HEIGHT_IMG_MAX 2464
#define HEIGHT_VID_MIN 64
#define HEIGHT_VID_MAX 960
#define DURATION_MIN 0
#define DURATION_MAX INT_MAX

class Picam {
	public:
		Picam(raspicam::RaspiCam_Cv cam, raspicam::RaspiCam_Still_Cv camStill);
		void captureImage();
		void captureImageFname(string filename);
		void captureVideo(int duration);
		void networkStream(int width, int height, int duration);
		void setImageResolution(int width, int height);
		void setVideoResolution(int width, int height);
		void setBrightness(int brightness);
		void setContrast(int contrast);
		void setSaturation(int saturation);
		void setGain(int gain);
		void setExposureTime(int speed);
		int processParameters(char parChar);
		char processCommand();
		void printCommands();
		
	private:
		raspicam::RaspiCam_Cv Camera;
		raspicam::RaspiCam_Still_Cv CameraStill;
};

#endif
