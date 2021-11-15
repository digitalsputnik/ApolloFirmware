import uasyncio as asyncio
import _thread
import time
import Render
import calib
import machine

from Empire.E_uArtnet_client import E_uArtnet_client as ArtNet

# ----- [0] Hardware interfaces

#i2c
i2c = machine.SoftI2C(scl=machine.Pin(22), sda=machine.Pin(23))

# fan @ pin(0)
fan = machine.PWM(machine.Pin(0),duty=1023)



# ----- [1] Output objects

# LED output RGBW
Output = Render.Render(i2cInterface=i2c, i2c_addr=79)


# ----- [2] Input objects

# WiFi
#wifiAp()
#wifiConnect("DS","SputnikulOn4Antenni")


# ArtNet
def artNetCallback(data_in):
    Output.setColor(data_in[0],data_in[1],data_in[2])

if db[b"ArtNet"] == b"On":
    ArtNetClientD = ArtNet(artNetCallback,debug=True)

# ----- [9] Software
time.sleep(2)
enable_all = machine.Pin(27, machine.Pin.OUT, value=1)



'''
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

def run_server(saddr, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.bind((saddr, port))

    try:
        while True:
            data, caddr = sock.recvfrom(1472)
            if data[0:5] == b'/REPL':
                end = data[12:].find(b'\x00\x00')
                message = data[12:].decode("utf-8").strip()
                
                print(message)
                eval(message)
                time.sleep_ms(10)
    finally:
        sock.close()



        
'''