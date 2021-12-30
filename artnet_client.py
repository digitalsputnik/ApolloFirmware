import uasyncio as asyncio
import socket
from struct import pack, unpack
import pysaver
import flags
import apa_controller as apa
import time

server = '0.0.0.0'
port = 6454

apa_color = (100,255,0)

callback = None

artnet_length = 4
artnet_start_offset = pysaver.load("artnet_start_offset", 0, True)

async def __setup__():
    global _socket
    update_apa()
    
    asyncio.create_task(toggle_artnet_offset_waiter())
    
    _socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    _socket.bind((server,port))
    _socket.setblocking(False)
    print("Art-Net Started. Offset - " + str(artnet_start_offset))
    
async def __slowloop__():
    global _socket, artnet_start_offset, callback
    update_apa()
    try:
        data, addr = _socket.recvfrom(1024)
        
        if is_artnet_packet(data):
            packet = ArtNetPacket(data)
            print("Data - " + str(packet.data))
        else:
            print("Received a non Art-Net packet")
    except Exception as e:
        await asyncio.sleep(0)
        
async def __slowerloop__():
    update_apa()
    
async def toggle_artnet_offset_waiter():
    global artnet_start_offset
    while True:
        await flags.program_short_flag.wait()
        
        artnet_start_offset += 5
        if (artnet_start_offset == 30):
            artnet_start_offset = 0
            
        pysaver.save("artnet_start_offset", artnet_start_offset)
        print("Art-Net Offset Changed - " + str(artnet_start_offset))

def update_apa():
    global artnet_start_offset, apa_color
    apa.unlock_all_leds()
    new_apa = int(artnet_start_offset/5)
    apa.set_led(new_apa, apa_color)
    apa.lock_led(new_apa)
    
def is_artnet_packet(data):
    if data[:8] != b'Art-Net\x00':
        return False
    else:
        return True

class ArtNetPacket:
    def __init__(self, data = None):
        if (data != None):
            self.op_code = hex(unpack('<H', data[8:10])[0])
            self.ver = unpack('!H', data[10:12])[0]
            self.sequence = data[12]
            self.physical = data[13]
            self.universe = unpack('<H', data[14:16])[0]
            self.length = unpack('!H', data[16:18])[0]
            
            self.data = (data[18], data[19], data[20], data[21])