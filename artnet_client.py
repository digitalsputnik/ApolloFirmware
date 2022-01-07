import uasyncio as asyncio
import socket
from struct import pack, unpack
import pysaver
import flags
import apa_controller as apa
import time
import io
import os
import tags

server = '0.0.0.0'
port = 6454

apa_color = (100,255,0)

callback = None

artnet_length = 4
artnet_start_offset = pysaver.load("artnet_start_offset", 0, True)

artnet_offset_waiter_task = None

async def __setup__():
    global _socket, artnet_offset_waiter_task
    
    update_apa()
    
    artnet_offset_waiter_task = asyncio.create_task(toggle_artnet_offset_waiter())
    
    _socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    _socket.bind((server,port))
    _socket.setblocking(False)
    print("Art-Net Started. Offset - " + str(artnet_start_offset))
    
async def __slowloop__():
    global _socket, artnet_start_offset, callback
    update_apa()
    try:
        data, address = _socket.recvfrom(1024)
        
        if is_artnet_packet(data):
            packet = ArtNetPacket(data)
            check_op_code(address, packet)
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
    
def check_op_code(address, packet):
    global op_codes
    if packet.op_code in op_codes:
        op_codes[packet.op_code](address, packet)
        
def color_from_artnet(address, packet):
    global artnet_start_offset, artnet_length
    if packet.universe == 0:
        color_data = packet.data[artnet_start_offset:artnet_start_offset+artnet_length]
        red = color_data[0]
        green = color_data[1]
        blue = color_data[2]
        white = color_data[3]
                
        if callback != None:
            callback(red,green,blue,white)
        
def artnet_repl(address, packet):
    global _socket
    correct_tag = False
    packet_tuple = parse_tuple(packet.data.decode())
            
    for tag in packet_tuple[0]:
        if (tags.has_tag(tag)):
            packet.data = packet_tuple[1]
            correct_tag = True
            
    if correct_tag:
        s = bytearray()
        os.dupterm(console_out(s))
        exec(packet.data, globals())
        _socket.sendto(bytes(s), address)
        os.dupterm(None)

op_codes = { "0x5000":color_from_artnet, "0x4000":artnet_repl }

def parse_tuple(string):
    try:
        s = eval(string)
        if type(s) == tuple:
            return s
    except:
        pass

class console_out(io.IOBase):

    def __init__(self, s):
        self.s = s

    def write(self, data):
        self.s += data
        return len(data)

    def readinto(self, data):
        return 0

class ArtNetPacket:
    def __init__(self, data = None):
        if (data != None):
            self.op_code = hex(unpack('<H', data[8:10])[0])
            self.ver = unpack('!H', data[10:12])[0]
            self.sequence = data[12]
            self.physical = data[13]
            self.universe = unpack('<H', data[14:16])[0]
            self.length = unpack('!H', data[16:18])[0]
            
            self.data = data[18:]