import uasyncio as asyncio
import _thread
import time
import Render
import machine
import calib
import os
import pysaver
from Lib.micropython_dotstar import DotStar as apa102

# ----- start of Empire modules init -------
from Empire.E_uArtnet_client import E_uArtnet_client as ArtNet
from Empire.E_uLM75 import E_uLM75 as LM75
#> next module will be here ...
# ----- end of Empire modules init ---------

artnet_offset_color = (100,255,0)

debounce_deadline=time.ticks_ms()
start_timer_bool = False
wifi_connected = False

artnet_offset = 0
artnet_offset = pysaver.load("artnet_offset")[0]

ap_mode = True
ap_mode = pysaver.load("ap_mode")[0]

# ----- [0] Hardware interfaces

def program_button_click(caller):
    global debounce_deadline, start_timer_bool
    #0.5sec debounce (the dome switch is slow to pop back therefore would create 2 clicks through bouncing
    if time.ticks_diff(time.ticks_ms(),debounce_deadline) > 0:
        debounce_deadline = time.ticks_add(time.ticks_ms(), 500)
        start_timer_bool = True

def main_loop():
    global program_timer, start_timer_bool
    while True:
        time.sleep(0.1)
        # Run click actions seperate from interrupts
        if start_timer_bool:
            start_timer_bool = False
            # Creating a virtual timer to differentiate between long and short presses 
            program_timer = machine.Timer(-1)
            program_timer.init(mode=machine.Timer.ONE_SHOT, period=500, callback=detect_short_or_long_press)
    
def detect_short_or_long_press(t):
    global debounce_deadline
    # If the button is released when the timer runs out, it was a short press.
    # Otherwise it was a long press
    if (program_button.value() == 1):
        increase_artnet_offset() # Short press action
    else:
        # Increasing long press debounce deadline to avoid wrong triggers during long press release
        while (program_button.value() == 0):
            debounce_deadline = time.ticks_add(time.ticks_ms(), 100)
            time.sleep(0.1)
            
        change_wifi_mode() # Long press action

def increase_artnet_offset():
    global artnet_offset
    artnet_offset += 5
    if (artnet_offset == 30):
        artnet_offset = 0
        
    update_apa_leds()
    ArtNetClientD.change_start_offset(artnet_offset)
    pysaver.save("artnet_offset", artnet_offset)
    
def change_wifi_mode():
    global ap_mode
    ap_mode = not ap_mode
    update_apa_leds()
    pysaver.save("ap_mode", ap_mode)
    machine.reset()
    
def update_apa_leds():
    if ap_mode:
        for i in range(6):
            APA102[i] = (0,0,int(i*30))
    else:
        if wifi_connected:
            for i in range(6):
                APA102[i] = (int(i*30),0,0)
        else:
            for i in range(6):
                APA102[i] = (0,int(i*30),0)
    
    APA102[int(artnet_offset/5)] = artnet_offset_color

def wifi_callback(connected):
    global wifi_connected
    wifi_connected = connected
    update_apa_leds()

_thread.start_new_thread(main_loop,())

# buttons
power_button = machine.Pin(35, machine.Pin.IN, machine.Pin.PULL_UP)

program_button = machine.Pin(34, machine.Pin.IN, machine.Pin.PULL_UP)
program_button.irq(trigger = machine.Pin.IRQ_FALLING, handler = program_button_click)

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
update_apa_leds()
# APA102[0]=(255,0,0) #1st led green channel on
# APA102.fill((10,10,10)) # all leds on low intencity
#card = machine.SDCard(width=1, slot=3)
#os.mount(card,"/sd")

# ----- [2] Input objects

def zfill(s, width):
    return '{:0>{w}}'.format(s, w=width)

# WiFi
if ap_mode:
    wifiAp()
else:
    apollo_found = False
    while (apollo_found == False):
        ssids = scan_ssids()
        smallest_apollo = 9999
        for ssid in ssids:
            if b"Apollo" in ssid[0]:
                if smallest_apollo > int(ssid[0][-4:]):
                    smallest_apollo = int(ssid[0][-4:])
                    apollo_found = True
        
        if apollo_found:
            selected_ssid = "Apollo" + zfill(str(smallest_apollo), 4)
            wifiConnect(selected_ssid,"", wifi_callback)
        else:
            print("Apollo not found")
            time.sleep(5)

# ArtNet
def artNetCallback(data_in):
    wbCalc = data_in[3]*33.33334+1500
    Output.setColor(data_in[0],data_in[1],data_in[2],wbIn=wbCalc)

ArtNetClientD = ArtNet(callback=artNetCallback, start=artnet_offset, debug=True)

# ----- [9] Software
#time.sleep(2)
enable_all = machine.Pin(27, machine.Pin.OUT, value=1)  