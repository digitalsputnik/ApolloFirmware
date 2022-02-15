import uasyncio as asyncio
from machine import Pin
from Lib.pushbutton import Pushbutton
import flags
import pysaver
import Data.pins as pins

# Button Pins
power_pin = pins.power_pin
program_pin = pins.program_pin

# Button actions
power_short = flags.power_short_flag.set # currently waited for in renderer
power_long = flags.power_long_flag.set # currently waited for in renderer
program_short = flags.program_short_flag.set # currently waited for in artnet_client
program_long = flags.program_long_flag.set # currently waited for in wifi

async def __setup__():
    asyncio.create_task(setup_buttons())
        
async def setup_buttons():
    global power_pin, program_pin
    
    power_button_pin_object = Pin(power_pin, Pin.IN, Pin.PULL_UP)
    program_button_pin_object = Pin(program_pin, Pin.IN, Pin.PULL_UP)
    
    if program_button_pin_object.value() is 0:
        while program_button_pin_object.value() is 0:
            await asyncio.sleep_ms(500)
        await asyncio.sleep_ms(500)
    
    power_button = Pushbutton(power_button_pin_object, True)
    program_button = Pushbutton(program_button_pin_object, True)
    
    if power_short != None:
        power_button.release_func(power_short)
    
    if power_long != None:
        power_button.long_func(power_long)
    
    if program_short != None:
        program_button.release_func(program_short)
    
    if program_long != None:
        program_button.long_func(program_long)