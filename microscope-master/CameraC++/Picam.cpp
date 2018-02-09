/***********************************************************************
 * 
 * C++ library for the Raspberry Pi camera module. This library uses the 
 * raspicam C++ API found here: https://github.com/cedricve/raspicam.
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
 * Functions
***********************************************************************/

Picam::Picam(raspicam::RaspiCam_Cv cam, raspicam::RaspiCam_Still_Cv camStill) : Camera(cam), CameraStill(camStill) {
	Camera.set(CV_CAP_PROP_FORMAT, CV_8UC3);
	cout << "Opening camera..." << endl;
	if (!Camera.open()) {
		cerr << "Error opening the camera" << endl;
	}
}

/* Capture a single image. */
void Picam::captureImage() {
	cv::Mat image;
	string filename;
	
	cout << "Input filename: " << endl;
	cin.clear();
	cin.ignore(10000, '\n');
	cin >> filename;
	
	cout << "Capturing image..." << endl;
	Camera.grab();
	cout << "A" << endl;
	Camera.retrieve(image);
	cout << "B" << endl;
	Camera.release();
	cout << "Image captured" << endl;
	cv::imwrite(filename,image);
	cout << "Image saved at ";
	cout << filename << endl;
}

/* Capture a single image with an input filename. */
void Picam::captureImageFname(string filename) {
	cv::Mat image;
	
	cout << "Capturing image..." << endl;
	CameraStill.grab();
	cout << "A" << endl;
	CameraStill.retrieve(image);
	cout << "B" << endl;
	CameraStill.release();
	cout << "Image captured" << endl;
	cv::imwrite(filename,image);
	cout << "Image saved at ";
	cout << filename << endl;
}

/* Capture a video using openCV video writer. */
void Picam::captureVideo(int duration) {
	cv::Mat image;
	int64_t startTime;
	int codec;
	bool isColour;
	double fps;
	string filename;
	int fno;
	int frate;
	
	cout << "Input filename: " << endl;
	cin.clear();
	cin.ignore(10000, '\n');
	cin >> filename;
	
	codec = CV_FOURCC('H','2','6','4'); // May change to H264
	isColour = (image.type() == CV_8UC3);
	fps = 24;
	image.cols = Camera.get(CV_CAP_PROP_FRAME_WIDTH);
	image.rows = Camera.get(CV_CAP_PROP_FRAME_HEIGHT);
	
	cv::VideoWriter writer;//filename, codec, fps, image.size(), isColour);
	writer.open(filename, codec, fps, image.size(), 1);
	
	//startTime = clock();
	startTime = cv::getTickCount();
	cout << "Recording started" << endl;
	
	//while ((clock() - startTime) < duration*CLOCKS_PER_SEC) {
	while ((cv::getTickCount() - startTime)/cv::getTickFrequency() < duration) {
		Camera.grab();
		Camera.retrieve(image);
		writer.write(image);
		
		fno++;
		if (fno % 10 == 0) {
			cout << writer.isOpened();
			cout << ", Frame ";
			cout << fno;
			cout << ", Time ";
			cout << (cv::getTickCount() - startTime)/cv::getTickFrequency() << endl;
		}
	}
	
	Camera.release();
	writer.release();
	frate = fno/duration;
	cout << "Recording finished" << endl;
	cout << "Framerate: ";
	cout << frate << endl;
	cout << "Video saved at ";
	cout << filename << endl;
}

/* Stream a video through a network. This is achieved through the command 
 * line, may be changed to work through openCV. */
void Picam::networkStream(int width, int height, int duration) {
	clock_t startTime;
	string netCommand;
	string sWidth;
	string sHeight;
	string sDuration;
	
	sWidth = to_string(width);
	sHeight = to_string(height);
	sDuration = to_string(duration*1000);
	netCommand = "raspivid -w " + sWidth + "-h " + sHeight + " -t " + sDuration + " -o - | nc my_server 8000";
	const char *netCmd = netCommand.c_str();
	
	startTime = clock();
	cout << "Streaming started" << endl;
	
	cout << netCommand << endl;
	system(netCmd);
	
	cout << "Streaming finished" << endl;
}

/* Set the camera image resoltion. */
void Picam::setImageResolution(int width, int height) {
	CameraStill.set (CV_CAP_PROP_FRAME_WIDTH, width);
	CameraStill.set (CV_CAP_PROP_FRAME_HEIGHT, height);
}

/* Set the camera video resoltion. */
void Picam::setVideoResolution(int width, int height) {
	Camera.set (CV_CAP_PROP_FRAME_WIDTH, width);
	Camera.set (CV_CAP_PROP_FRAME_HEIGHT, height);
}

/* Set the camera brightness. */
void Picam::setBrightness(int brightness) {
	Camera.set (CV_CAP_PROP_BRIGHTNESS, brightness);
	CameraStill.set (CV_CAP_PROP_BRIGHTNESS, brightness);
	cout << "Brightness changed" << endl;
}

/* Set the camera contrast. */
void Picam::setContrast(int contrast) {
	Camera.set (CV_CAP_PROP_CONTRAST, contrast);
	CameraStill.set (CV_CAP_PROP_CONTRAST, contrast);
	cout << "Contrast changed" << endl;
}

/* Set the camera saturation. */
void Picam::setSaturation(int saturation) {
	Camera.set (CV_CAP_PROP_SATURATION, saturation);
	CameraStill.set (CV_CAP_PROP_SATURATION, saturation);
	cout << "Saturation changed" << endl;
}

/* Set the camera saturation. */
void Picam::setGain(int gain) {
	Camera.set (CV_CAP_PROP_GAIN, gain);
	CameraStill.set (CV_CAP_PROP_GAIN, gain);
	cout << "Gain changed" << endl;
}

/* Set the camera saturation. */
void Picam::setExposureTime(int speed) {
	Camera.set (CV_CAP_PROP_EXPOSURE, speed);
	CameraStill.set (CV_CAP_PROP_EXPOSURE, speed);
	cout << "Exposure time changed" << endl;
}

/* Process camera parameters. */
int Picam::processParameters(char parChar) {
	int parValue;
	int currValue;
	int minValue;
	int maxValue;
	string parString;
	
	switch(parChar) {
		case 'W':
			parString = "width";
			currValue = CameraStill.get(CV_CAP_PROP_FRAME_WIDTH);
			minValue = WIDTH_IMG_MIN;
			maxValue = WIDTH_IMG_MAX;
			break;
		
		case 'H':
			parString = "height";
			currValue = CameraStill.get(CV_CAP_PROP_FRAME_HEIGHT);
			minValue = HEIGHT_IMG_MIN;
			maxValue = HEIGHT_IMG_MAX;
			break;
			
		case 'w':
			parString = "width";
			currValue = Camera.get(CV_CAP_PROP_FRAME_WIDTH);
			minValue = WIDTH_VID_MIN;
			maxValue = WIDTH_VID_MAX;
			break;
		
		case 'h':
			parString = "height";
			currValue = Camera.get(CV_CAP_PROP_FRAME_HEIGHT);
			minValue = HEIGHT_VID_MIN;
			maxValue = HEIGHT_VID_MAX;
			break;
		
		case 'B':
			parString = "brightness";
			currValue = Camera.get(CV_CAP_PROP_BRIGHTNESS);
			minValue = BRIGHTNESS_MIN;
			maxValue = BRIGHTNESS_MAX;
			break;
		
		case 'C':
			parString = "contrast";
			currValue = Camera.get(CV_CAP_PROP_CONTRAST);
			minValue = CONTRAST_MIN;
			maxValue = CONTRAST_MAX;
			break;
		
		case 'S':
			parString = "saturation";
			currValue = Camera.get(CV_CAP_PROP_SATURATION);
			minValue = SATURATION_MIN;
			maxValue = SATURATION_MAX;
			break;
		
		case 'G':
			parString = "gain";
			currValue = Camera.get(CV_CAP_PROP_GAIN);
			minValue = GAIN_MIN;
			maxValue = GAIN_MAX;
			break;
		
		case 'X':
			parString = "exposure time";
			currValue = Camera.get(CV_CAP_PROP_EXPOSURE);
			minValue = EXPOSURE_MIN;
			maxValue = EXPOSURE_MAX;
			break;
			
		case 'D':
			parString = "duration";
			currValue = 0;
			minValue = DURATION_MIN;
			maxValue = DURATION_MAX;
			break;
		
		default:
			currValue = -2;
	}

	cout << "Input ";
	cout << parString;
	cout << " (Current: ";
	cout << currValue;
	cout << ", Min: ";
	cout << minValue;
	cout << ", Max: ";
	cout << maxValue;
	cout << "): ";

	cin.clear();
	cin.ignore(10000, '\n');
	cin >> parValue;
	
	while (cin.fail() || parValue < minValue || parValue > maxValue) {
		if (cin.fail()) {
			cout << "Error: Not a number" << endl;
		}
		else if (parValue < minValue) {
			cout << "Error: Value is less than minimum" << endl;
		}
		else if (parValue > maxValue) {
			cout << "Error: Value is greater than maximum" << endl;
		}
		
		cout << "Input ";
		cout << parString;
		cout << " (Current: ";
		cout << currValue;
		cout << ", Min: ";
		cout << minValue;
		cout << ", Max: ";
		cout << maxValue;
		cout << "): ";

		cin.clear();
		cin.ignore(10000, '\n');
		cin >> parValue;
	}
	
	return parValue;
}

/* Process command from the terminal. */
char Picam::processCommand() {
	char command;
	
	cout << "Input camera command: ";
	cin >> command;
	
	return toupper(command);
}

/* Print a list of commands. */
void Picam::printCommands() {
	cout << "\nList of commands:" << endl;
	cout << "	B: Set brightness" << endl;
	cout << "	C: Set contrast" << endl;
	cout << "	G: Set gain" << endl;
	cout << "	H: Help" << endl;
	cout << "	I: Capture an image" << endl;
	cout << "	N: Stream to network (not implemented)" << endl;
	cout << "	Q: Quit program" << endl;
	cout << "	S: Set saturation" << endl;
	cout << "	V: Capture a video" << endl;
	cout << "	X: Set exposure time\n" << endl;
}
