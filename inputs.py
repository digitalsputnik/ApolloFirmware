import uasyncio as asyncio
from machine import Pin
from Lib.pushbutton import Pushbutton
import flags
import pysaver
import Data.pins as pins

# Button Pins
_power_pin = pins.power_pin
_program_pin = pins.program_pin

# Button actions
_power_short = flags.power_short_flag.set # currently waited for in renderer
_power_long = flags.power_long_flag.set # currently waited for in renderer
_program_short = flags.program_short_flag.set # currently waited for in artnet_client
_program_long = flags.program_long_flag.set # currently waited for in wifi

async def __setup__():
    global _power_pin, _program_pin
    
    # Create button objects
    _power_button = Pushbutton(Pin(_power_pin, Pin.IN, Pin.PULL_UP), True)
    _program_button = Pushbutton(Pin(_program_pin, Pin.IN, Pin.PULL_UP), True)
    
    # Set button actions if actions arent None
    if _power_short != None:
        _power_button.release_func(_power_short)
    
    if _power_long != None:
        _power_button.long_func(_power_long)
    
    if _program_short != None:
        _program_button.release_func(_program_short)
    
    if _program_long != None:
        _program_button.long_func(_program_long)