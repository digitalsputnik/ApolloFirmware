import uasyncio as asyncio
import socket
from struct import pack, unpack
import pysaver
import flags
import led_controller as led
import time
import io
import os
import tags
import wifi
import rewriter

server = '0.0.0.0'
port = 6454

led_color = (100,255,0)

callback = None

artnet_length = 5
artnet_start_offset = pysaver.load("artnet_start_offset", 0, True)
artnet_start_universe = pysaver.load("artnet_start_universe", 0, True)

artnet_offset_waiter_task = None

async def __setup__():
    global _socket, artnet_offset_waiter_task
    
    update_led()
    
    artnet_offset_waiter_task = asyncio.create_task(toggle_artnet_offset_waiter())
    
    _socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    _socket.bind((server,port))
    _socket.setblocking(False)
    print("Art-Net Started. Offset - " + str(artnet_start_offset))
    
async def __slowloop__():
    global _socket, artnet_start_offset, callback
    update_led()
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
    update_led()
    
async def toggle_artnet_offset_waiter():
    global artnet_start_offset
    while True:
        await flags.program_short_flag.wait()
        
        artnet_start_offset += 5
        if (artnet_start_offset == 30):
            artnet_start_offset = 0
            
        pysaver.save("artnet_start_offset", artnet_start_offset)
        print("Art-Net Offset Changed - " + str(artnet_start_offset))

def update_led():
    global artnet_start_offset, led_color
    led.unlock_all_leds()
    new_led = int(artnet_start_offset/5)
    led.set_led(new_led, led_color)
    led.lock_led(new_led)
    
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
    global artnet_start_offset, artnet_length, artnet_start_universe
    if packet.universe == artnet_start_universe:
        color_data = packet.data[artnet_start_offset:artnet_start_offset+artnet_length]
        red = color_data[0]
        green = color_data[1]
        blue = color_data[2]
        white = color_data[3]
        fx = color_data[4]
                
        if callback != None:
            callback(red,green,blue,white,fx)
        
def artnet_repl(address, packet):
    global _socket
    correct_tag = False
    packet_tuple = parse_tuple(packet.data.decode())
    identifier = packet_tuple[0]
    sent_tags = packet_tuple[1]
    command = packet_tuple[2]
    
    if (len(sent_tags) == 0):
        correct_tag = True
    else:
        for tag in sent_tags:
            if (tags.has_tag(tag)):
                correct_tag = True
    
    if correct_tag:
        safe = filter_incoming_command(command)
        
        s = bytearray()
        os.dupterm(console_out(s))
        
        if safe:
            exec(command, globals())
        else:
            print("Some parts of your command aren't authorized")
            
        result = bytes(s)
        if (len(result) > 0):
            _socket.sendto(str((wifi.device_id, identifier, result)).encode(), address)
        os.dupterm(None)

def filter_incoming_command(command):
    if not rewriter.authenticated:
        filters = ['open(', 'rewriter.authenticated', 'rewriter.rewriter_setup', 'rewriter.rewriter_password', 'rewriter.receiving_data', 'pysaver']
    
        safe = True
        
        command = command.replace(' ', '')
        command = command.replace('\t', '')
    
        for fil in filters:
            if fil in command:
                safe = False
            
        return safe
    else:
        return True

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