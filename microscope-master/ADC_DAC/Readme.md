# ADC_DAC

This folder contains python code to run the ADC_DAC module on the Raspberry Pi.

## Files

- ADC_DAC_Pi.py: Pure Python library adaptation of the DAQT7_Objective library for the Raspberry Pi. Achieves a sample rate of 12 kHz.

- ADC_DAC_PiC.py: C version of the library adaptation using a Python wrapper. Achieves a sample rate of 30 kHz.

- ADCTest.py: Test for the ADC_DAC_Pi library.

- ADCTestC.py: Test for the ADC_DAC_PiC library.

- ABE_ADCDACPi.c: C library to interface with the ADC_DAC module.

- ABE_ADCDACPi.h: Header file for the C library.

## Instructions

The ADC_DAC module of the Raspberry Pi may be used instead of the DAQT7 in a python code by replacing the line:

	import DAQT7_Objective as DAQ

with:

	import ADC_DAC_PiC

as well as replacing the line:

	DAQ1 = DAQ.DetectDAQT7()

with:

	DAQ1 = ADC_DAC_PiC.DetectPi()

The library has three operational functions:

	writePort(self, Port, Volt)
	readPort(self, Port)
	streamRead(self, scanRate, scansPerRead, Port)

The writePort function outputs a voltage <Volt> on the desired channel <Port>.
The voltage must be between a range of 0 V to 3.3 V.
If a voltage higher than 3.3 V is specified, the output voltage will be 3.3 V.
The Port may be either a string ('DAC0' or 'DAC1'), or an integer (1 or 2).

The readPort function returns the voltage on a desired channel <Port>.
The port may be either a string ('AIN0' or 'AIN1'), or an integer (1 or 2).

The streamRead function returns an array of voltages on a desired channel or channels.
The channel <Port> may be either a string ('AIN0' or 'AIN1'), or an integer (1 or 2).
Both channels may be used by specifying a list of ports.
The length of the array is equal to <scansPerRead> multiplied by the number of channels.
The rate at which data is obtained is specified by the <scanRate> parameter.
The scan rate must be less than 25000 kHz if one channel is specified, or 12500 kHz if two channels are specified.
If a higher scan rate is specified, then the actual scan rate will vary between 25-30 kHz.

The library must be closed at the end of the code, by using the close() function.

## Raspberry Pi Installation

The ADC_DAC code requires the ADCDACPi library. This can be installed by running the commands:

	cd Documents
	git clone https://github.com/abelectronicsuk/ABElectronics_Python_Libraries.git
	export PYTHONPATH=${PYTHONPATH}:~/Documents/ABElectronics_Python_Libraries/ADCDACPi/

The ADC_DAC_PiC code requires the ABE_ADCDACPi library .so file. This file can be obtained by compiling the library:

	gcc -shared -o libABE_ADCDACPi.so -fPIC ABE_ADCDACPi.c

## Current progress

- The Python wrapped C version of the code is able to achieve a sample rate of just over 30 kHz.

- Moving a bunch Python-side code to the C-side could increase the sample rate to 50-100 kHz.

## Issues

In some cases, the duration of reading may need to be doubled in order to obtain the desired duration.
