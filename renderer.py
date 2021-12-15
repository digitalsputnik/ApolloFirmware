import uasyncio as asyncio
import machine
import artnet_client

red_pin = 33
green_pin = 25
blue_pin = 26
white_pin = 27

red = 10
green = 10
blue = 10
white = 1500

_pwm = []

async def __setup__():
    global _pwn, red_pin, green_pin, blue_pin, white_pin
    artnet_client.callback = set_color
    _pwm.append(machine.PWM(machine.Pin(red_pin)))
    _pwm.append(machine.PWM(machine.Pin(green_pin)))
    _pwm.append(machine.PWM(machine.Pin(blue_pin)))
    _pwm.append(machine.PWM(machine.Pin(white_pin)))
    _pwm[0].freq(19000)

async def __loop__():
    global _pwm, red, green, blue, white
    _pwm[0].duty(red) 
    _pwm[1].duty(green)
    _pwm[2].duty(blue)
    _pwm[3].duty(white)

def set_color(r_in=0, g_in=0, b_in=0, wb_in=0):
    global red, green, blue, white
    
    red = r_in
    green = g_in
    blue = b_in
    white = wb_in
    