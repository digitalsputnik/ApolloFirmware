import io
import os
import socket
from struct import pack, unpack
import uasyncio as asyncio
import led_controller as led
import pysaver
import wifi
import rewriter
import tags
import flags

# Artnet ip & port. Default is broadcast ip and port 6454
_server = '0.0.0.0'
_port = 6454

# Color of led indicator on informative led strip (apa/neopixel)
_led_color = (100,255,0)

# Length of artnet data group
_artnet_length = 5
_artnet_fx = pysaver.load("artnet_fx", [1,0], True)
_artnet_control = pysaver.load("artnet_control", [0,0], True)

# for debuging purposes
# todo, split the answer for last packet as it is too long for one aswer packet
_last_fx = None
_last_control = None

# Callbacks
callback_control = None
callback_fx = None

# Button press listener task
artnet_offset_waiter_task = None

async def __setup__():
    global _socket, artnet_offset_waiter_task
    update_led()
    
    artnet_offset_waiter_task = asyncio.create_task(toggle_artnet_offset_waiter())
    
    _socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    _socket.bind((_server,_port))
    _socket.setblocking(False)
    
    print("Art-Net Started. Offset - " + str(_artnet_control[1]))
    
async def __slowloop__():
    global _socket, callback_control
    update_led()
    
    try:
        _data, _address = _socket.recvfrom(1024)
        
        # Check if incoming packet is an artnet packet
        if is_artnet_packet(_data):
            # Decode packet into an object
            _packet = ArtNetPacket(_data)
            # Check packet type
            check_op_code(_address, _packet)
        else:
            print("Received a non Art-Net packet")
    except Exception as e:
        await asyncio.sleep(0)
        
async def __slowerloop__():
    update_led()
    
async def toggle_artnet_offset_waiter():
    global _artnet_control
    # Non terminating loop for button press detection
    while True:
        # On button press, program_short_flag is set which stops waiting.
        await flags.program_short_flag.wait()
        
        # Update artnet offset.
        _artnet_control[1] += 5
        if (_artnet_control[1] == 30):
            _artnet_control[1] = 0
        
        # Save updated offset
        pysaver.save("artnet_control", [_artnet_control[0],_artnet_control[1]])
        
        print("Art-Net Offset Changed - " + str(_artnet_control[1]))

# Function to check if a packet is artnet
def is_artnet_packet(_data):
    if _data[:7] != b'Art-Net':
        return False
    else:
        return True

# Function to check op_code in packet, supported op_codes are in a list on line 193
def check_op_code(_address, _packet):
    global _op_codes
    if _packet.op_code in _op_codes:
        _op_codes[_packet.op_code](_address, _packet)

# Handle color artnet packet
def color_from_artnet(_address, _packet):
    global _artnet_control, _artnet_length, _last_control, _last_fx, _last_values
    
    # Check if universe is fx universe
    if _packet.universe == _artnet_fx[0]:
        _color_data = _packet.data[_artnet_fx[1]:_artnet_control[0]+3]
        _last_fx = (_packet,_color_data)
        
        # if callback is not null, call callback with received data
        if callback_fx != None:
            callback_fx(_color_data[0],_color_data[1],_color_data[2])
    
    # Check if universe is color universe
    if _packet.universe == _artnet_control[0]:
        _color_data = _packet.data[_artnet_control[1]:_artnet_control[1]+_artnet_length]
        _last_control = (_packet,_color_data)
        
        # Parse color data
        _red = _color_data[0]
        _green = _color_data[1]
        _blue = _color_data[2]
        _white = _color_data[3]
        _fx = _color_data[4]
        
        # if callback is not null, call callback with received data
        if callback_control != None:
            callback_control(_red,_green,_blue,_white,_fx)

# Handle artnet repl packet
def artnet_repl(_address, _packet):
    global _socket
    _correct_tag = False
    
    # Parse incoming data into variables
    _packet_tuple = parse_tuple(_packet.data.decode())
    
    # Unique uuid for each packet to verify answers
    _identifier = _packet_tuple[0]
    
    # Tags on which the command should be ran
    _sent_tags = _packet_tuple[1]
    _command = _packet_tuple[2]
    
    # If tags is an empty list, the command should be ran on all devices in network
    if (len(_sent_tags) == 0):
        _correct_tag = True
    else:
        for _tag in _sent_tags:
            if (tags.has_tag(_tag)):
                _correct_tag = True
    
    if _correct_tag:
        # Some actions are not allowed until authorized in rewriter.
        # Here we check if any of the forbidden actions are in the received command
        _safe = filter_incoming_command(_command)
        
        _s = bytearray()
        os.dupterm(console_out(_s))
        
        if _safe:
            try:
                exec(_command, globals())
            except Exception as _err:
                print(_err)
        else:
            print("Some parts of your command aren't authorized")
            
        _result = bytes(_s)
        if (len(_result) > 0):
            # Send back printed data, if any was printed
            _socket.sendto(str((wifi.device_id, _identifier, _result)).encode(), _address)
        os.dupterm(None)

def filter_incoming_command(_command):
    if not rewriter.authenticated:
        # Keywords that are not allowed in the command
        _filters = ['open(', 'rewriter.authenticated', 'rewriter._rewriter_setup', 'rewriter._rewriter_password', 'rewriter._receiving_data', 'pysaver']
    
        _safe = True
        
        _command = _command.replace(' ', '')
        _command = _command.replace('\t', '')
    
        for _filter in _filters:
            if _filter in _command:
                _safe = False
            
        return _safe
    else:
        return True

# Packet op_codes with functions to run when an op_code is detected
_op_codes = { "0x5000":color_from_artnet, "0x4000":artnet_repl }

# Function to update status on apa/neopixel leds
def update_led():
    global _artnet_control, _led_color
    led.unlock_all_leds()
    _new_led = int(_artnet_control[1]/5)
    led.set_led(_new_led, _led_color)
    led.lock_led(_new_led)

# Helper function to parse a tuple from a string
def parse_tuple(_string):
    try:
        _s = eval(_string)
        if type(_s) == tuple:
            return _s
    except:
        pass

# Helper class to read printed data
class console_out(io.IOBase):

    def __init__(self, s):
        self.s = s

    def write(self, data):
        self.s += data
        return len(data)

    def readinto(self, data):
        return 0

# Artnet Packet data class
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