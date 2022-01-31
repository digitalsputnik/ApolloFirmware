import uasyncio as asyncio
import Data.pins as pins
import machine

main_loop_frequency = 5
slow_loop_frequency = 10
slower_loop_frequency = 1000

import_modules = ['fan_controller', 'lm75', 'inputs', 'renderer', 'wifi', 'artnet_client']

async def main_loop():
    global main_tasks, main_loop_frequency
    while True:
        for task in main_tasks:
            asyncio.create_task(task())
        await asyncio.sleep_ms(main_loop_frequency)
        
async def slow_loop():
    global slow_tasks, slow_loop_frequency
    while True:
        for task in slow_tasks:
            asyncio.create_task(task())
        await asyncio.sleep_ms(slow_loop_frequency)
        
async def slower_loop():
    global slower_tasks, slower_loop_frequency
    while True:
        for task in slower_tasks:
            asyncio.create_task(task())
        await asyncio.sleep_ms(slower_loop_frequency)

async def setup():
    global import_modules, setup_tasks, main_tasks, slow_tasks, slower_tasks
    
    # Run custom script if program button isn't held down
    # TODO - Indicate to user when script has been ignored to avoid accidental wifi connection type changes (default program button action)
    # NOTE - It seems like checking for pin value slows boot time, needs further research
    program_button = machine.Pin(pins.program_pin, machine.Pin.IN, machine.Pin.PULL_UP)
    
    if program_button.value() is 1:
        import custom_script
    
    setup_tasks = []
    main_tasks = []
    slow_tasks = []
    slower_tasks = []
    
    for import_module in import_modules:
        imported_module = __import__(import_module)
        
        setup = getattr(imported_module, "__setup__", None)
        if callable(setup):
            setup_tasks.append(setup)
            
        loop_obj = getattr(imported_module, "__loop__", None)
        if callable(loop_obj):
            main_tasks.append(loop_obj)
            
        slow_loop_obj = getattr(imported_module, "__slowloop__", None)
        if callable(slow_loop_obj):
            slow_tasks.append(slow_loop_obj)
            
        slower_loop_obj = getattr(imported_module, "__slowerloop__", None)
        if callable(slower_loop_obj):
            slower_tasks.append(slower_loop_obj)
    
    for task in setup_tasks:
        asyncio.create_task(task())
    
    main = asyncio.create_task(main_loop())
    slow = asyncio.create_task(slow_loop())
    slower = asyncio.create_task(slower_loop())
    await main

asyncio.run(setup())