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
import renderer
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
artnet_control = pysaver.load("artnet_control", [0,0], True)

artnet_offset_waiter_task = None
update_leds = True

multi_packet_list = {}
_max_len = 29640000

async def __setup__():
    global _socket, artnet_offset_waiter_task
    
    artnet_offset_waiter_task = asyncio.create_task(toggle_artnet_offset_waiter())
    
    update_led()
    
    for i in range(6):
        if ('ch' + str(i+1) in tags.tags):
            tags.remove_tag('ch' + str(i+1))
            
    tags.add_tag('ch' + str(int(artnet_control[1]/10 + 1)))
    
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
        
        tags.remove_tag('ch' + str(int(artnet_control[1]/10 + 1)))
        
        artnet_control[1] += 10
        artnet_fx[1] += 10
        if (artnet_control[1] == 60):
            artnet_control[1] = 0
            artnet_fx[1] = 0
        
        update_led()
        
        tags.add_tag('ch' + str(int(artnet_control[1]/10 + 1)))
        
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
        color_data = packet.data[artnet_fx[1]:artnet_fx[1]+3]
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
    global _socket, _max_len
    if packet.data.decode().startswith('('):
        print("Received old packet")
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
    else:
        monet_packet = MonetPacket(packet.data)
        if monet_packet.Total == 1:
            handle_single_packet(monet_packet, address)
        elif (monet_packet.Total * 456) > _max_len:
            print("Too big")
        else:
            handle_multi_packet(monet_packet, address)
        
def handle_single_packet(packet, address):
    if tags.has_tag(packet.Tag) or len(packet.Tag) == 0:
        safe = filter_incoming_command(packet.Data)
        
        s = bytearray()
        os.dupterm(console_out(s))
        
        if safe:
            execute_command(packet.Data)
        else:
            print("Some parts of your command aren't authorized")
            
        result = bytes(s).decode()
        
        if (len(result) > 0):
            if (len(result) > 456):
                packet_count = int(len(result)/456) + 1
                packets = []
            
                for i in range(packet_count):
                    packets.append(MonetPacket(packet.Tag, packet.UUID, i + 1, packet_count, result[i*456:(i+1)*456]))
                
                for i, pack in enumerate(reversed(packets)):
                    response_packet = bytearray()
                    response_packet.extend(generate_header(0x40))
                    response_packet.extend(pack.as_byte())
                    _socket.sendto(response_packet, address)
            else:
                response_packet = bytearray()
                response_packet.extend(generate_header(0x40))
                monet_packet = MonetPacket(packet.Tag, packet.UUID, 1, 1, result)
                response_packet.extend(monet_packet.as_byte())
                _socket.sendto(response_packet, address)
        os.dupterm(None)

def execute_command(command):
    try:
        exec(command, globals())
    except Exception as err:
        print(err)

def handle_multi_packet(packet, address):
    global multi_packet_list
    if packet.UUID not in multi_packet_list:
        multi_packet_list[packet.UUID] = []
            
    exists = False
            
    for old_packet in multi_packet_list[packet.UUID]:
        if old_packet == packet:
            exists = True
            
    if not exists:
        multi_packet_list[packet.UUID].append(packet)
            
    if len(multi_packet_list[packet.UUID]) == packet.Total:
        all_data = ""
            
        for pack in sorted(multi_packet_list[packet.UUID], key=lambda x: x.Index):
            all_data = all_data + pack.Data
            
        handle_single_packet(MonetPacket(packet.Tag, packet.UUID, 1, 1, all_data), address)
        
        multi_packet_list.pop(packet.UUID, None)

def generate_header(op_code):
    '''
    Generates artnet packet header with correct op_code
    '''
    header = bytearray()
    header.extend(bytearray('Art-Net', 'utf8'))
    header.append(0x0)
    header.append(0x0)
    header.append(op_code)
    header.append(0x0)
    header.append(0x0)
    header.append(0x0)
    header.append(0x0)
    header.append(0x1) #Universe
    header.append(0x0)
    header.append(0x0) 
    header.append(0x0)
    return header

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
        
        #handle the max led count
        active_led = int(artnet_control[1]/10)
        if active_led<=led.led_count:
            led.set_single_led(active_led, led.FOREGROUND_LAYER, (255,100,0))
        else:
            led.clear_foreground()
    
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
            
class MonetPacket:
    
    def __init__(self, *args, **kwargs):
        if isinstance(args[0], str):
            self.Tag = args[0]
            self.UUID = args[1]
            self.Index = args[2]
            self.Total = args[3]
            self.Data = args[4]
        else:
            data = args[0]
            self.Tag  = data[:16].decode().rstrip('\x00')
            self.UUID  = data[16:52].decode().rstrip('\x00')
            self.Index  = (data[52 + 1] << 8) + data[52]
            self.Total  = (data[54 + 1] << 8) + data[54]
            self.Data  = data[56:].decode()
        
    def as_byte(self):
        packet_data = bytearray(56 + len(self.Data))
        
        packet_data[0:16] = self.Tag.encode()
        packet_data[16:52] = self.UUID.encode()
        packet_data[52:53] = self.Index.to_bytes(2, 'little')
        packet_data[54:55] = self.Total.to_bytes(2, 'little')
        packet_data[56:] = self.Data.encode()
        
        return packet_data
    
    def __eq__(self, other):
        return self.UUID == other.UUID and self.Index == other.Index