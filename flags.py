import uasyncio as asyncio

power_short_flag = asyncio.ThreadSafeFlag()
power_long_flag = asyncio.ThreadSafeFlag()
program_short_flag = asyncio.ThreadSafeFlag()
program_long_flag = asyncio.ThreadSafeFlag()
    