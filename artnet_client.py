import uasyncio as asyncio
import socket
from struct import pack, unpack
import pysaver
import flags
import time
import io
import os
import tags
import wifi
import rewriter
import led_controller as led

server = '0.0.0.0'
port = 6454

callback_control = None
callback_fx = None

# for debuging purposes
# todo, split the answer for last packet as it is too long for one aswer packet
last_fx = None
last_control = None

artnet_length = 5
artnet_fx = pysaver.load("artnet_fx", [100,0], True)
artnet_control = pysaver.load("artnet_control", [1,0], True)

artnet_offset_waiter_task = None
update_leds = True

async def __setup__():
    global _socket, artnet_offset_waiter_task
    
    artnet_offset_waiter_task = asyncio.create_task(toggle_artnet_offset_waiter())
    
    update_led()
    
    _socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    _socket.bind((server,port))
    _socket.setblocking(False)
    print("Art-Net Started. Offset - " + str(artnet_control[1]))
    
async def __slowloop__():
    global _socket, callback_control
    try:
        data, address = _socket.recvfrom(1024)
        
        if is_artnet_packet(data):
            packet = ArtNetPacket(data)
            check_op_code(address, packet)
        else:
            print("Received a non Art-Net packet")
    except Exception as e:
        await asyncio.sleep(0)
    
async def toggle_artnet_offset_waiter():
    global artnet_control, artnet_fx
    while True:
        await flags.program_short_flag.wait()
        
        artnet_control[1] += 5
        artnet_fx[1] += 5
        if (artnet_control[1] == 30):
            artnet_control[1] = 0
            artnet_fx[1] = 0
        
        update_led()
        pysaver.save("artnet_control", [artnet_control[0],artnet_control[1]])
        pysaver.save("artnet_fx", [artnet_fx[0],artnet_fx[1]])
        print("Art-Net Offset Changed - " + str(artnet_control[1]))
        print("Art-Net FX Channel Offset Changed - " + str(artnet_fx[1]))
    
def is_artnet_packet(data):
    if data[:7] != b'Art-Net':
        return False
    else:
        return True
    
def check_op_code(address, packet):
    global op_codes
    if packet.op_code in op_codes:
        op_codes[packet.op_code](address, packet)
        
def color_from_artnet(address, packet):
    global artnet_control, artnet_length, last_control, last_fx, last_values
    
    if packet.universe == artnet_fx[0]:
        color_data = packet.data[artnet_fx[1]:artnet_control[0]+3]
        last_fx = (packet,color_data)
        
        if callback_fx != None:
            callback_fx(color_data[0],color_data[1],color_data[2])
    
    # controller universe
    if packet.universe == artnet_control[0]:
        color_data = packet.data[artnet_control[1]:artnet_control[1]+artnet_length]
        last_control = (packet,color_data)
        
        red = color_data[0]
        green = color_data[1]
        blue = color_data[2]
        white = color_data[3]
        fx = color_data[4]
                
        if callback_control != None:
            callback_control(red,green,blue,white,fx)
        
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
            try:
                exec(command, globals())
            except Exception as err:
                print(err)
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

def update_led():
    global artnet_control, led_color
    if update_leds:
        led.clear_foreground()
        led.set_single_led(int(artnet_control[1]/5), led.FOREGROUND_LAYER, (255,100,0))
    
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