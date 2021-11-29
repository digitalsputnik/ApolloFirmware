import time

timestring = str(time.ticks_ms()) + ", "

import machine
import os
import pysaver
from Lib.micropython_dotstar import DotStar as apa102

from Empire.E_uLM75 import E_uLM75 as LM75

timestring += str(time.ticks_ms()) + ", "

# buttons
debounce_deadline=time.ticks_ms()

# Power button:
def onoff_handler(caller):
    global save_time_analysis, APA102, _on, debounce_deadline
    #0.5sec debounce (the dome switch is slow to pop back therefore would create 2 clicks through bouncing
    if time.ticks_diff(time.ticks_ms(),debounce_deadline) > 0:
        debounce_deadline = time.ticks_add(time.ticks_ms(), 500)
    
        save_time_start = time.ticks_ms()
    
        # If lamp was switched on, it will be switched off
        if _on:
            _on = False
            pysaver.save("_on", _on)
            #APA102[0]=(0,0,0)
        # If lamp was switched off, it will be switched on
        else:
            _on = True
            pysaver.save("_on", _on)
            #APA102[0]=(255,0,0)
            
        save_time = time.ticks_ms() - save_time_start
            
        save_time_analysis = []
        save_time_analysis = pysaver.load("save_time_analysis")
        save_time_analysis.append(save_time)
    
        pysaver.save("save_time_analysis", save_time_analysis)
            
        print(str(save_time_analysis))
            
    
power_button = machine.Pin(35, machine.Pin.IN, machine.Pin.PULL_UP)
power_button.irq(trigger = machine.Pin.IRQ_FALLING, handler = onoff_handler)

# i2c
i2c = machine.SoftI2C(scl=machine.Pin(22), sda=machine.Pin(23))
spi = machine.SoftSPI(sck=machine.Pin(26), mosi=machine.Pin(25), miso=machine.Pin(0))

# fan @ pin(0)
fan = machine.PWM(machine.Pin(0),duty=255)

# Sensors
led_temp = LM75(i2c,79)

timestring += str(time.ticks_ms()) + ", "

#Load saved data
_on = True
pysaver.load("_on")

timestring += str(time.ticks_ms()) + ", "

# APA102 indicator
APA102 = apa102(spi,6)

if _on:
    APA102[0]=(255,0,0)
else:
    APA102[0]=(0,0,0)
    
timestring += str(time.ticks_ms())

# Saving boot time analysis to a file in Data folder.
# Data is saved as a list of tuple's with each tuple containing five time values in milliseconds
# The values are "Boot" "All Imports" "Before Load" "After Load" "Finish"]

boot_time_analysis = []

boot_time_analysis = pysaver.load("boot_time_analysis")
boot_time_analysis.append(tuple(map(int, timestring.split(', '))))
    
pysaver.save("boot_time_analysis", boot_time_analysis)

# The values can be exported using the function below and pasted into google colab for graph overview

def export_boot_time_analysis():
    global boot_time_analysis
    boot_time_analysis = []
    boot_time_analysis = pysaver.load("boot_time_analysis")
    print(str(boot_time_analysis))

def export_save_time_analysis():
    global save_time_analysis
    save_time_analysis = []
    save_time_analysis = pysaver.load("save_time_analysis")
    print(str(save_time_analysis))
    
def reset_boot_time_analysis():
    global boot_time_analysis
    boot_time_analysis = []
    pysaver.save("boot_time_analysis", boot_time_analysis)
    print(str(boot_time_analysis))

def reset_save_time_analysis():
    global save_time_analysis
    save_time_analysis = []
    pysaver.save("save_time_analysis", save_time_analysis)
    print(str(save_time_analysis))

# APA102[0]=(255,0,0) #1st led green channel on
# APA102.fill((10,10,10)) # all leds on low intencity
