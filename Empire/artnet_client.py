# loop disabled buttons currently, don't know yet why

import uasyncio as asyncio
import socket
import pysaver

artnet_toggled_flag = asyncio.ThreadSafeFlag()

artnet_start_offset = 0
artnet_length = 4

callback = None

async def __setup__():
    global _socket
    asyncio.create_task(toggle_artnet_offset_waiter())
    
    _socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    _socket.bind(("0.0.0.0",6454))
    print("Art-Net Started")

async def toggle_artnet_offset_waiter():
    global artnet_start_offset
    while True:
        await artnet_toggled_flag.wait()
        
        artnet_start_offset += 5
        if (artnet_start_offset == 30):
            artnet_start_offset = 0
            
        pysaver.save("artnet_start_offset", artnet_start_offset)
        print("Art-Net Offset Changed - " + str(artnet_start_offset))

async def __loop__disabled():
    global _socket, artnet_start_offset, callback
    try:
        data, addr = _socket.recvfrom(1024)
        if len(data) > 20:
            AN_header = data[0:7]
            AN_opcode = data[8:10]
            AN_universe = data[14:16]
            AN_length = data[17]
            
            check_state = 0
            if AN_header == b"Art-Net":
                check_state = 1
            if AN_opcode == b'\x00P' and check_state == 1:
                check_state = 2
            if AN_universe == b'\x00\x00' and check_state == 2:
                check_state = 99
             
            if check_state == 99:
                dataStart = 18 + artnet_start_offset
                dataEnd = 18 + artnet_start_offset + artnet_length
                complete_data = data[dataStart:dataEnd]
                if callback != None:
                    callback(complete_data)
                else:
                    print(str(complete_data[0]) + ", " + str(complete_data[1]) + ", " + str(complete_data[2]) + ", " + str(complete_data[3]))
              
    except Exception as e:
        print(str(e))
        await asyncio.sleep(0.1)