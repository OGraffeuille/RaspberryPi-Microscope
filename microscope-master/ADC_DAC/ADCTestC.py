'''
Script to test the functionality of the Raspberry Pi ADC_DAC CTypes module.

Author: Damon Hutley
Date: 14th December 2016
'''

import ADC_DAC_PiC

# Initialise the ADC_DAC module
adcmod = ADC_DAC_PiC.DetectPi()
port1 = ['AIN0']
port2 = ['AIN1']
portAll = ['AIN0','AIN1']

## Read Channel 1 and 2
#read1, time1 = adcmod.readPort(port1)
#read2, time2 = adcmod.readPort(port2)
#print(read1, time1)
#print(read2, time2)

## Estimate ADC rate
#rate = 1/float(time2 - time1)
#print(rate)

# Stream read from channel 0
scansPerRead = 100000
scanRate = 10000
print("Starting stream")
read, start, end = adcmod.streamRead(scanRate,scansPerRead,port1)
print("Scans: " + str(len(read)))
print("Rate: " + str(len(read)/float(end-start)) + " Hz")
print("Stream ended")

# Stream read from channel 1
scansPerRead = 100000
scanRate = 10000
print("Starting stream")
read, start, end = adcmod.streamRead(scanRate,scansPerRead,port2)
print("Scans: " + str(len(read)))
print("Rate: " + str(len(read)/float(end-start)) + " Hz")
print("Stream ended")

# Stream read from both channels
scansPerRead = 100000
scanRate = 10000
print("Starting stream")
read, start, end = adcmod.streamRead(scanRate,scansPerRead,portAll)
print("Scans: " + str(len(read)))
print("Rate: " + str(len(read)/float(end-start)) + " Hz")
print("Stream ended")
