from boot import Output
import uasyncio as asyncio
import _thread
import time


class ArtNetClient:
    '''Ultra simple Art-Net client 
    
    Ignore all cheks and just push 1st 4 values in 1st DMX universe onto the LEDs
    '''
    
    
    def __init__(self, renderer):
        self._render = renderer
        # TODO check if inet is up
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._socket.bind((sta_if.ifconfig()[0],6454))
        #self._socket.bind(("127.0.0.1",6454))
        self._thread_id = _thread.get_ident()
        #self._sock.setblocking(False)

        _thread.start_new_thread(self.udpReader,())

    def udpReader(self): 
        while True:
            try:
                data, addr = self._socket.recvfrom(1024)
                # check if it is an artnet packet
                if len(data) > 20:
                    header = data[0:7]
                    if header == b"Art-Net":
                        self._render.setColor(data[18],data[19],data[20])
            except Exception as e:
                print(e)



def toggleArtnetBoot():
    if db[b"ArtNet"] == b"On":
        db[b"ArtNet"] = b"Off"
        db.close()
        f.write("mydb")
        machine.reset()
    else:
        db[b"ArtNet"] = b"On"
        db.close()
        f.write("mydb")
        machine.reset()    

if db[b"ArtNet"] == b"On":
    wifiAp()
    global ArtNetClientD
    ArtNetClientD = ArtNetClient(Output)     