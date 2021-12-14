import machine
import time
import wifi
import artnet_client

# Button Pins
power_pin = 22
program_pin = 23

# Button actions
power_short = None
power_long = None
program_short = artnet_client.artnet_toggled_flag.set
program_long = wifi.mode_changed_flag.set

start_power_debouce_timer = False
start_program_debouce_timer = False

# Debouncing needs work, should remove all time.sleep()'s
debounce_deadline=time.ticks_ms()

async def __setup__():
    global power_pin, program_pin
    setup_power_button(power_pin, power_button_click)
    setup_program_button(program_pin, program_button_click)

def power_button_click(caller):
    global debounce_deadline, start_power_debouce_timer
    if time.ticks_diff(time.ticks_ms(),debounce_deadline) > 0:
        debounce_deadline = time.ticks_add(time.ticks_ms(), 500)
        start_power_debouce_timer = True

def program_button_click(caller):
    global debounce_deadline, start_program_debouce_timer
    if time.ticks_diff(time.ticks_ms(),debounce_deadline) > 0:
        debounce_deadline = time.ticks_add(time.ticks_ms(), 500)
        start_program_debouce_timer = True

async def __loop__():
    global start_program_debouce_timer, start_power_debouce_timer
    
    if start_power_debouce_timer:
        start_power_debouce_timer = False
        power_timer = machine.Timer(-1)
        power_timer.init(mode=machine.Timer.ONE_SHOT, period=500, callback=lambda t:detect_short_or_long_press("power"))
        
    if start_program_debouce_timer:
        start_program_debouce_timer = False
        program_timer = machine.Timer(-1)
        program_timer.init(mode=machine.Timer.ONE_SHOT, period=500, callback=lambda t:detect_short_or_long_press("program"))
    
def detect_short_or_long_press(button):
    global debounce_deadline
    if button == "program":
        if program_button.value() == 1:
            if program_short != None:
                program_short()
        else:
            while (program_button.value() == 0):
                debounce_deadline = time.ticks_add(time.ticks_ms(), 100)
                time.sleep(0.1)
            if program_long != None:
                program_long()
    else:
        if power_button.value() == 1:
            if power_short != None:
                power_short()
        else:
            while (power_button.value() == 0):
                debounce_deadline = time.ticks_add(time.ticks_ms(), 100)
                time.sleep(0.1)
            if power_long != None:
                power_long()
        
def setup_power_button(pin, callback):
    global power_button
    power_button = machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_UP)
    power_button.irq(trigger = machine.Pin.IRQ_FALLING, handler = callback)

def setup_program_button(pin, callback):
    global program_button
    program_button = machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_UP)
    program_button.irq(trigger = machine.Pin.IRQ_FALLING, handler = callback)