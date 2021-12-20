import uasyncio as asyncio
from machine import Pin
from Lib.pushbutton import Pushbutton
import flags

# Button Pins
power_pin = 35
program_pin = 34

# Button actions
power_short = flags.power_short_flag.set
power_long = flags.power_long_flag.set
program_short = flags.program_short_flag.set # currently waited for in artnet_client
program_long = flags.program_long_flag.set # currently waited for in wifi

async def __setup__():
    global power_pin, program_pin
    
    power_button = Pushbutton(Pin(power_pin, Pin.IN, Pin.PULL_UP), True)
    program_button = Pushbutton(Pin(program_pin, Pin.IN, Pin.PULL_UP), True)
    
    if power_short != None:
        power_button.release_func(power_short)
    
    if power_long != None:
        power_button.long_func(power_long)
    
    if program_short != None:
        program_button.release_func(program_short)
    
    if program_long != None:
        program_button.long_func(program_long)