import uasyncio as asyncio
import wifi
import inputs
import renderer

default_main_loop_frequency = 0.1
default_side_loop_frequency = 1

setup_tasks = [wifi.setup, inputs.setup, renderer.setup]
main_tasks = [inputs.loop]
side_tasks = [renderer.loop]

async def main_loop(frequency = default_main_loop_frequency):
    global main_tasks, main_frequency
    main_frequency = frequency
    while True:
        for task in main_tasks:
            await asyncio.create_task(task())
        await asyncio.sleep(main_frequency)
        
async def side_loop(frequency = default_side_loop_frequency):
    global side_tasks, side_frequency
    side_frequency = frequency
    while True:
        for task in side_tasks:
            await asyncio.create_task(task())
        await asyncio.sleep(side_frequency)

async def setup():
    global setup_tasks
    for task in setup_tasks:
        await asyncio.create_task(task())
    
    main = asyncio.create_task(main_loop())
    side = asyncio.create_task(side_loop())
    await main

asyncio.run(setup())