'''
Adaptation of the DAQT7_Objective library for the Raspberry Pi, using CTypes for speed gains.

Author: Damon Hutley
Date: 14th December 2016
'''


import ctypes
import time
import numpy as np
import sys


class DetectPi:
	
	def __init__(self):
		'''
		Initialise ADC-DAC Pi. The DAC gain factor is set to 1, which allows 
		the DAC output voltage to be set between 0 and 2.048 V. The DAC gain 
		factor may also be set to 2, which gives an output range of 0 to 3.3 V.
		'''
		
		self.Error = 0
		
		try:
			# Import the adc_dac C library
			self.adclib = ctypes.CDLL('/home/pi/Documents/PhysicsSummer/ADC_DAC/libABE_ADCDACPi.so')
			
			# Initialise ADC and DAC SPI
			self.adclib.open_adc()
			self.adclib.open_dac()
			
			# Set reference voltage to 3.3 V and DAC gain to 2
			self.adclib.set_adc_refvoltage(ctypes.c_double(3.3))
			self.adclib.set_dac_gain(ctypes.c_int(2))
			
			print("ADC_DAC_Pi is ready\n")
		except:
			self.Error = 1
			raise Exception("Initialisation failed")
		
		return
		
	
	def getDetails(self):
		'''
		Return details of ADC_DAC Pi. This function does not currently return 
		any details, but this may change later.
		'''
		
		return
		
	
	def writePort(self, Port, Volt):
		'''
		Write values to a DAC pin. Values may be written to either channel 1 
		or channel 2. The maximum voltage is specified by the gain factor.
		Note: Setting a voltage greater than 3.3 V will result in an output 
		voltage of 3.3 V.
		'''
		
		# Ensure port is of type list
		if type(Port) == str or type(Port) == int:
			Port = [Port]
		
		# Convert DAQT7 DAC ports to DAC Pi channels
		if "DAC0" in Port or 1 in Port:
			channel = 1
		elif "DAC1" in Port or 2 in Port:
			channel = 2
		else:
			self.Error = 1
			raise Exception("Port must be a string ('DAC0' or 'DAC1'), or an int (1 or 2)")
		
		if Volt > 3.299:
			print("Voltage exceeds maximum limit. Reducing to 3.3 V.")
			maxVolt = 3.299
		else:
			maxVolt = Volt
		
		# Set DAC output voltage <Volt> on channel <channel>
		self.adclib.set_dac_voltage(ctypes.c_double(maxVolt), ctypes.c_int(channel))
		
		return
		
	
	def readPort(self, Port):
		'''
		Read values from an ADC pin. Values may be read from either channel 1 
		or channel 2. 
		'''
		
		# Ensure port is of type list
		if type(Port) == str or type(Port) == int:
			Port = [Port]
		
		# Convert DAQT7 AIN ports to ADC Pi channels
		if "AIN0" in Port or 1 in Port:
			channel = 1
		elif "AIN1" in Port or 2 in Port:
			channel = 2
		else:
			self.Error = 1
			raise Exception("Port must be a string ('AIN0' or 'AIN1'), or an int (1 or 2)")
		
		# Read voltage from channel <channel> in single ended mode
		self.adclib.read_adc_voltage.restype = ctypes.c_double
		voltRead = self.adclib.read_adc_voltage(ctypes.c_int(channel), ctypes.c_int(0))
		
		return np.float(voltRead), time.time()
		
	
	def streamRead(self, scanRate, scansPerRead, Port):
		'''
		Read analogue input values from an ADC pin, in stream mode.
		'''
		
		# Ensure port is of type list
		if type(Port) == str or type(Port) == int:
			Port = [Port]
		
		# Convert DAQ ports to ADC channels
		channel = []
		for p in Port:
			if p == "AIN0" or 1 in Port:
				channel.append(1)
			elif p == "AIN1" or 2 in Port:
				channel.append(2)
			else:
				self.Error = 1
				raise Exception("Port must be a string ('AIN0' or 'AIN1'), or an int (1 or 2)")
		
		# Initialise array and time values
		Read = [[], 1, 2]
		StartingMoment = 0
		FinishingMoment = 0
		scansPerRead = int(scansPerRead)
		
		# Allow for alternation between multiple ports
		portIndex = 0
		totIndex = 0
		portLength = len(channel)
		totScans = scansPerRead*portLength
		
		# Determine timing characteristics
		duration = scansPerRead/float(scanRate)
		dt = 1/float(scanRate*portLength)
		
		# Loop for the duration
		StartingMoment = time.time()
		lastReadTime = time.clock()
		offerr = 15e-6
		while totIndex < totScans:
			# Read the ADC value and append to an array
			self.adclib.read_adc_voltage.restype = ctypes.c_double
			voltRead = self.adclib.read_adc_voltage(ctypes.c_int(channel[portIndex]), ctypes.c_int(0))
			Read[0].append(voltRead)
			portIndex = (portIndex + 1) % portLength
			totIndex += 1
			
			# Wait for the program to run at the correct frequency
			readTime = time.time()
			if readTime - lastReadTime < dt:
				secs = long((dt - time.time() + lastReadTime - offerr) * 1e9)
				lastReadTime = readTime
				startt = time.time()
				self.adclib.c_sleep(ctypes.c_long(secs))
			else:
				lastReadTime = readTime
			
			
		# Calculate and print elapsed time
		FinishingMoment = time.time()
		print ('Elapsed time %f seconds' % (FinishingMoment - StartingMoment))
		
		return Read, StartingMoment, FinishingMoment
		
	
	def close(self):
		'''
		Close ADC-DAC Pi.
		'''
		
		self.adclib.close_adc()
		self.adclib.close_dac()


		

