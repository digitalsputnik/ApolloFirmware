import uasyncio as asyncio
import _thread
import time
import Render
import machine
import calib
import os
import boot
from Lib.micropython_dotstar import DotStar as apa102

# ----- start of Empire modules init -------
from Empire.E_uArtnet_client import E_uArtnet_client as ArtNet
from Empire.E_uLM75 import E_uLM75 as LM75
#> next module will be here ...
# ----- end of Empire modules init ---------

# ----- [0] Hardware interfaces

# buttons
power_button = machine.Pin(34, machine.Pin.IN, machine.Pin.PULL_UP)
program_button = machine.Pin(35, machine.Pin.IN, machine.Pin.PULL_UP)

# i2c
i2c = machine.SoftI2C(scl=machine.Pin(22), sda=machine.Pin(23))
spi = machine.SoftSPI(sck=machine.Pin(26), mosi=machine.Pin(25), miso=machine.Pin(0))

# fan @ pin(0)
fan = machine.PWM(machine.Pin(0),duty=255)

# Sensors
led_temp = LM75(i2c,78)


# ----- [1] Output objects

# LED output RGBW
Output = Render.Render(calib.LampCalibartion,led_temp)

# APA102 indicator
APA102 = apa102(spi,6)
# APA102[0]=(255,0,0) #1st led green channel on
# APA102.fill((10,10,10)) # all leds on low intencity
#card = machine.SDCard(width=1, slot=3)
#os.mount(card,"/sd")

# ----- [2] Input objects

# WiFi
wifiAp()
#wifiConnect("Apollo0001","dsputnik")



# ArtNet
def artNetCallback(data_in):
    wbCalc = data_in[3]*33.33334+1500
    Output.setColor(data_in[0],data_in[1],data_in[2],wbIn=wbCalc)

if db[b"ArtNet"] == b"On":
    ArtNetClientD = ArtNet(artNetCallback,debug=True)

# ----- [9] Software
#time.sleep(2)
enable_all = machine.Pin(27, machine.Pin.OUT, value=1)



# ----- [X] Try new and wierd stuff here:
def toggleArtnetBoot():
    if db[b"ArtNet"] == b"On":
        db[b"ArtNet"] = b"Off"
        db.close()
        f.write("mydb")
        machine.reset()
    else:
        db[b"ArtNet"] = b"On"
        db.close()
        f.write("mydb")
        machine.reset()    
# apa animation

apa_array= ((0,0,32),(2,0,16),(4,0,8),(8,0,4),(16,0,2),(32,0,0))
APA102[0] = apa_array[0]
APA102[1] = apa_array[1]
APA102[2] = apa_array[2]
APA102[3] = apa_array[3]
APA102[4] = apa_array[4]
APA102[5] = apa_array[5]