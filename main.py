import uasyncio as asyncio

main_loop_frequency = 0.1
side_loop_frequency = 1

import_modules = ['inputs', 'wifi', 'artnet_client', 'renderer']

async def main_loop(frequency = main_loop_frequency):
    global main_tasks, main_frequency
    main_frequency = frequency
    while True:
        for task in main_tasks:
            asyncio.create_task(task())
        await asyncio.sleep(main_frequency)
        
async def side_loop(frequency = side_loop_frequency):
    global side_tasks, side_frequency
    side_frequency = frequency
    while True:
        for task in side_tasks:
            asyncio.create_task(task())
        await asyncio.sleep(side_frequency)

async def setup():
    global import_modules, setup_tasks, main_tasks, side_tasks
    
    setup_tasks = []
    main_tasks = []
    side_tasks = []
    
    for import_module in import_modules:
        imported_module = __import__(import_module)
        
        setup = getattr(imported_module, "__setup__", None)
        if callable(setup):
            setup_tasks.append(setup)
            
        loop = getattr(imported_module, "__loop__", None)
        if callable(loop):
            main_tasks.append(loop)
            
        slow_loop = getattr(imported_module, "__slowloop__", None)
        if callable(slow_loop):
            side_tasks.append(slow_loop)
    
    for task in setup_tasks:
        asyncio.create_task(task())
    
    main = asyncio.create_task(main_loop())
    side = asyncio.create_task(side_loop())
    await main

asyncio.run(setup())