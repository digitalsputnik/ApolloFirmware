import uasyncio as asyncio
import machine
import lm75 as temp
import pysaver
import Data.pins as pins

fan = None
fan_pin = pins.fan_pin
fan_duty = 0

min_fan_duty = 0
max_fan_duty = 1023

target_temp = 500
step = 128
reaction_delay_s = 5

async def __setup__():
    global fan, fan_pin, fan_duty
    fan = machine.PWM(machine.Pin(fan_pin),duty=fan_duty)
    asyncio.create_task(temp_point_chaser_loop())

async def temp_point_chaser_loop():
    global fan, fan_duty, target_temp, min_fan_duty, max_fan_duty, step, reaction_delay_s
    while True:
        await asyncio.sleep(reaction_delay_s)
        current_temp = temp.current_temp
        diff = current_temp - target_temp
        
        if diff < 0:
            fan_duty = fan_duty - step

        if diff > 0:
            fan_duty = fan_duty + step
            
        if fan_duty > max_fan_duty:
            fan_duty = max_fan_duty
        
        if fan_duty < min_fan_duty:
            fan_duty = min_fan_duty
            
        fan.duty(fan_duty)