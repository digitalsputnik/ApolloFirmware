import uasyncio as asyncio

async def __setup__():
    print("render setup")

async def __slowloop__():
    print("rendering")