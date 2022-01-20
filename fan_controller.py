import uasyncio as asyncio
import machine
import lm75 as temp
import pysaver
import Data.pins as pins

_fan = None
_fan_pin = pins.fan_pin
_fan_duty = 0

_min_fan_duty = 0
_max_fan_duty = 1023

# Temperature that should be kept, if temp is over 500, ramp up fans
_target_temp = 500

# Increment size when changing fan speed
_step = 128

# Fan point chaser reaction delay
_reaction_delay_s = 5

# Fan point chaser task
fan_point_chaser_task = None

async def __setup__():
    global _fan, _fan_pin, _fan_duty, fan_point_chaser_task
    # Creating fan object
    _fan = machine.PWM(machine.Pin(_fan_pin),duty=_fan_duty)
    # Creating fan point chaser task
    fan_point_chaser_task = asyncio.create_task(temp_point_chaser_loop())

async def temp_point_chaser_loop():
    global _fan, _fan_duty, _target_temp, _min_fan_duty, _max_fan_duty, _step, _reaction_delay_s
    while True:
        await asyncio.sleep(_reaction_delay_s)
        # Check current temperature
        _current_temp = temp.current_temp
        # Find the difference between target and current temperatures
        _diff = _current_temp - _target_temp
        
        # Adjust fan duty based on the current and target temperatures
        if _diff < 0:
            _fan_duty = _fan_duty - _step

        if _diff > 0:
            _fan_duty = _fan_duty + _step
        
        if _fan_duty > _max_fan_duty:
            _fan_duty = _max_fan_duty
        
        if _fan_duty < _min_fan_duty:
            _fan_duty = _min_fan_duty
            
        _fan.duty(_fan_duty)

# Function to get current fan speed in percentage
def speed():
    global _fan_duty, _max_fan_duty
    return (_max_fan_duty / _fan_duty) * 100