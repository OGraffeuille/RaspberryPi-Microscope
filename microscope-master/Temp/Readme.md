# Temp

This folder contains modifications to the DanielFlashReading code.

## Files

- DanielFlashReading.py: Modified to reduce the noise from the DAQ input signals.

- DAQT7_Objective.py: DAQ library. Slightly modified to get correct timing.

- SeaBreeze_Objective.py: Spectrometer library.

- ThorlabsPM100_Objective.py: Power meter library.

## Instructions

Open a terminal and type the following commands:

	cd Documents/Damon/PhysicsSummer/Temp
	python DanielFlashReading.py
	
If the PhysicsSummer folder does not exist, download the folder by running the command:

	git clone https://github.com/dhutley/PhysicsSummer
	cd PhysicsSummer/Temp
	python DanielFlashReading.py

## Modifications

- Calculations are added to convert the analogue thermocouple input into temperature. This calculation is based on the opamp gain.

- Every 100 samples of each DAQ input signal is averaged, in order to reduce noise.

- The StreamRead function is modified to obtain the correct finishing time, in order to display the correct time on the plot x axis.

- The electrical opamp circuit is modified to increase the gain on the temperature input. The potentiometers are set such that R1 = 10.16 kOhms, and R2 = 138.3 Ohms.
