import uasyncio as asyncio
import machine

# Frequency in milliseconds of the main loop
_main_loop_frequency = 5

# Frequency in milliseconds of the slow loop
_slow_loop_frequency = 10

# Frequency in milliseconds of the slower loop
_slower_loop_frequency = 100

# List of modules to import
import_modules = ['fan_controller', 'lm75', 'inputs', 'renderer', 'wifi', 'artnet_client']

# Main loop - all __loop__() functions in imported modules will be run in this loop
async def main_loop():
    global main_tasks, _main_loop_frequency
    while True:
        for task in main_tasks:
            asyncio.create_task(task())
        await asyncio.sleep_ms(_main_loop_frequency)

# Slow loop - all __slowloop__() functions in imported modules will be run in this loop
async def slow_loop():
    global slow_tasks, _slow_loop_frequency
    while True:
        for task in slow_tasks:
            asyncio.create_task(task())
        await asyncio.sleep_ms(_slow_loop_frequency)
        
# Slower loop - all __slowerloop__() functions in imported modules will be run in this loop
async def slower_loop():
    global slower_tasks, _slower_loop_frequency
    while True:
        for task in slower_tasks:
            asyncio.create_task(task())
        await asyncio.sleep_ms(_slower_loop_frequency)

async def setup():
    global import_modules, main_tasks, slow_tasks, slower_tasks
    
    # Lists of task to run in loops
    setup_tasks = []
    main_tasks = []
    slow_tasks = []
    slower_tasks = []
    
    # Importing modules and checking for existing functions
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
    
    # Running Setup Tasks - These are functions in imported modules called __setup__()
    for task in setup_tasks:
        asyncio.create_task(task())
    
    # Starting loops
    main = asyncio.create_task(main_loop())
    slow = asyncio.create_task(slow_loop())
    slower = asyncio.create_task(slower_loop())
    
    await main

# Start Setup
asyncio.run(setup())