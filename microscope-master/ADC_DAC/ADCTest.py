'''
Script to test the functionality of the Raspberry Pi ADC_DAC module.

Author: Damon Hutley
Date: 14th December 2016
'''

import ADC_DAC_Pi

# Initialise the ADC_DAC module
adcmod = ADC_DAC_Pi.DetectPi()
port1 = ['AIN0']
port2 = ['AIN1']

# Read Channel 1 and 2
read1, time1 = adcmod.readPort(port1)
read2, time2 = adcmod.readPort(port2)
print(read1, time1)
print(read2, time2)

# Estimate ADC rate
rate = 1/float(time2 - time1)
print(rate)
