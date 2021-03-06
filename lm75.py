import uasyncio as asyncio
import machine
from math import floor
import pysaver
import Data.pins as pins
import renderer

i2c = None

i2c_clock_pin = pins.i2c_clock_pin
i2c_data_pin = pins.i2c_data_pin

i2c_address = pins.i2c_address
error = "None"
last_results = (0,0)
current_temp = 0
temp_values = []

async def __setup__():
    global i2c
    i2c = machine.SoftI2C(scl=machine.Pin(i2c_clock_pin), sda=machine.Pin(i2c_data_pin))
    asyncio.create_task(temp_loop())

async def temp_loop():
    global temp_values, current_temp
    while True:
        await asyncio.sleep(1)
        if len(temp_values) < 7:
            temp_values.append(get_temp())
        else:
            temp_values.pop(0)
            temp_values.append(get_temp())
            temp_list = temp_values.copy()
            temp_list.sort(reverse = True)
            current_temp = temp_list[3]
            print(temp_list)
        

def get_output():
    global i2c, i2c_address
    """Return raw output from the LM75 sensor."""
    output = i2c.readfrom(i2c_address, 2)
    return output[0], output[1]

def get_temp():
    global last_results, error
    """Return a int, the temp in Celsius x 10"""
    try:
        temp = get_output()
        last_results = (int(temp[0]), floor(int(temp[1]) / 23))
        return int(last_results[0]*10+last_results[1])
    except Exception as e:
        error = e
        return renderer.max_op_temp + 10 # This is so the lamp would turn off to avoid burning