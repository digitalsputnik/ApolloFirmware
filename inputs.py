from machine import Pin
import uasyncio as asyncio
from Lib.pushbutton import Pushbutton
import artnet_client
import wifi

# Button Pins
power_pin = 22
program_pin = 23

# Button actions
power_short = None
power_long = None
program_short = None
program_long = None

async def __setup__():
    global power_pin, program_pin
    power_button_pin = Pin(power_pin, Pin.IN, Pin.PULL_UP)
    program_button_pin = Pin(program_pin, Pin.IN, Pin.PULL_UP)
    power_button = Pushbutton(power_button_pin, True)
    program_button = Pushbutton(program_button_pin, True)
    power_button.debounce_ms = 50
    program_button.debounce_ms = 50

    set_actions()
    
    if power_short != None:
        power_button.release_func(power_short)
    
    if power_long != None:
        power_button.long_func(power_long)
    
    if program_short != None:
        program_button.release_func(program_short)
    
    if program_long != None:
        program_button.long_func(program_long)
        
def set_actions():
    global artnet_toggled_flag, mode_changed_flag, program_short, program_long
    program_short = artnet_client.artnet_toggled_flag.set
    program_long = wifi.mode_changed_flag.set