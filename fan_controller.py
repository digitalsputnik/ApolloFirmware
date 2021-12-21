import machine

fan = None
fan_pin = 0
fan_duty = 255

async def __setup__():
    global fan, fan_pin, fan_duty
    fan = machine.PWM(machine.Pin(fan_pin),duty=fan_duty)