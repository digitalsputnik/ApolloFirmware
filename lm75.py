'''
Temperature sensor handler module
'''

import uasyncio as asyncio
import machine
from math import floor
import Data.pins as pins

_i2c = None

# Pin assignments
_i2c_clock_pin = pins.i2c_clock_pin
_i2c_data_pin = pins.i2c_data_pin
_i2c_address = pins.i2c_address

_error = "None"
_last_results = (0,0)
_temp_values = []

# Public current temp value
current_temp = 0

# Temperature checking loop
temperature_loop_task = None

async def __setup__():
    global _i2c, temperature_loop_task
    # Creating temperature sensor object
    _i2c = machine.SoftI2C(scl=machine.Pin(_i2c_clock_pin), sda=machine.Pin(_i2c_data_pin))
    # Creating temperature checking loop
    temperature_loop_task = asyncio.create_task(temp_loop())

async def temp_loop():
    global _temp_values, _current_temp
    while True:
        # Temperature is checked in one second intervals
        await asyncio.sleep(1)
        
        # Checking is done by comparing 7 last values,
        # sorting them and finding the middlepoint to avoid random accidental wrong values
        
        # Wait until 7 values have been read 
        if len(_temp_values) < 7:
            _temp_values.append(get_temp())
        else:
            # Popping the first value of the previous values list
            _temp_values.pop(0)
            # Adding a new temperature value to the list
            _temp_values.append(get_temp())
            # Copying the list to another variable for sorting
            _temp_list = _temp_values.copy()
            _temp_list.sort(reverse = True)
            # Taking middlepoint of the list as the current temperature variable
            _current_temp = _temp_list[3]
        

def get_output():
    global _i2c, _i2c_address
    # Return raw output from the LM75 sensor
    _output = _i2c.readfrom(_i2c_address, 2)
    return _output[0], _output[1]

def get_temp():
    global _last_results, _error
    # Return a int, the temp in Celsius x 10
    try:
        _temp = get_output()
        _last_results = (int(_temp[0]), floor(int(_temp[1]) / 23))
        return int(_last_results[0]*10+_last_results[1])
    except Exception as _e:
        _error = _e
        return 220 # Average room temperature is 22 degrees celcius