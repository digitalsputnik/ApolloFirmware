import uasyncio as asyncio
import socket
import pysaver
import flags

server = '0.0.0.0'
port = 6454

artnet_start_offset = pysaver.load("artnet_start_offset")
artnet_length = 4

callback = None

async def __setup__():
    global _socket
    asyncio.create_task(toggle_artnet_offset_waiter())
    
    _socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    _socket.bind((server,port))
    _socket.setblocking(False)
    print("Art-Net Started. Offset - " + str(artnet_start_offset))

async def toggle_artnet_offset_waiter():
    global artnet_start_offset
    while True:
        await flags.program_short_flag.wait()
        
        artnet_start_offset += 5
        if (artnet_start_offset == 30):
            artnet_start_offset = 0
            
        pysaver.save("artnet_start_offset", artnet_start_offset)
        print("Art-Net Offset Changed - " + str(artnet_start_offset))

async def __slowloop__():
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
                
                red = complete_data[0]*4
                green = complete_data[1]*4
                blue = complete_data[2]*4
                white = complete_data[3]*4
                
                if callback != None:
                    callback(red,green,blue,white)
                else:
                    print(str(red) + ", " + str(green) + ", " + str(blue) + ", " + str(white))
              
    except Exception as e:
        await asyncio.sleep(0)