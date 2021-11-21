import uasyncio as asyncio
import _thread
import time
import Render
import machine
import calib
import os
from Lib.micropython_dotstar import DotStar as apa102

# ----- start of Empire modules init -------
from Empire.E_uArtnet_client import E_uArtnet_client as ArtNet
from Empire.E_uLM75 import E_uLM75 as LM75
#> next module will be here ...
# ----- end of Empire modules init ---------

# ----- [0] Hardware interfaces

# buttons
debounce_deadline=time.ticks_ms()

def onoff_handler(caller):
    global c, _on, debounce_deadline
    if time.ticks_diff(time.ticks_ms(),debounce_deadline) > 0:
        debounce_deadline = time.ticks_add(time.ticks_ms(), 500)
        if _on:
            try:
                os.remove("_color.py")
            except Exception as e:
                pass
            myfile = open ("_color.py", "w")
            myfile.write("c="+str(Output._rgbt)+"\n")
            myfile.write("_on = False")
            myfile.close()
            enable_all.off()
            _on = False
        else:
            try:
                os.remove("_color.py")
            except Exception as e:
                pass
            myfile = open ("_color.py", "w")
            myfile.write("c="+str(c)+"\n")
            myfile.write("_on = True")
            myfile.close()
            enable_all.on()
            _on = True
    
power_button = machine.Pin(35, machine.Pin.IN, machine.Pin.PULL_UP)
power_button.irq(trigger = machine.Pin.IRQ_FALLING, handler = onoff_handler)

program_button = machine.Pin(34, machine.Pin.IN, machine.Pin.PULL_UP)

# i2c
i2c = machine.SoftI2C(scl=machine.Pin(22), sda=machine.Pin(23))
spi = machine.SoftSPI(sck=machine.Pin(26), mosi=machine.Pin(25), miso=machine.Pin(0))

# fan @ pin(0)
fan = machine.PWM(machine.Pin(0),duty=255)

# Sensors
led_temp = LM75(i2c,79)


# ----- [1] Output objects

# LED output RGBW
time.sleep(0.1)
Output = Render.Render(calib.LampCalibartion,led_temp)
# if _color.py exists restore values and put them on
try:
    from _color import c
    from _color import _on
except Exception as e:
    c=(0,0,0)
    _on=True

Output.setColor(c[0],c[1],c[2])
if _on:
    enable_all = machine.Pin(27, machine.Pin.OUT, value=1)
else:
    enable_all = machine.Pin(27, machine.Pin.OUT, value=0)

# APA102 indicator
APA102 = apa102(spi,6)
# APA102[0]=(255,0,0) #1st led green channel on
# APA102.fill((10,10,10)) # all leds on low intencity
# meie plaat
#card = machine.SDCard(width=1, slot=3, sck=machine.Pin(14), cs=machine.Pin(13), miso=machine.Pin(12), mosi=machine.Pin(15))
# wroom kit
#card = machine.SDCard(slot=3, width=1, sck=machine.Pin(14), cs=machine.Pin(13), miso=machine.Pin(2), mosi=machine.Pin(15))
#card = machine.SDCard(slot=3) #eidf dokumentatsioonis on 

#os.mount(card,"/sd")

# ----- [2] Input objects

# WiFi
wifiAp()
#wifiConnect("DS","SputnikulOn4Antenni")



# ArtNet
def artNetCallback(data_in):
    Output.setColor(data_in[0],data_in[1],data_in[2])

if db[b"ArtNet"] == b"On":
    ArtNetClientD = ArtNet(artNetCallback,debug=True)

# ----- [9] Software
#time.sleep(2)




# ----- [X] Try new and wierd stuff here:
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
# apa animation

apa_array= ((0,0,32),(2,0,16),(4,0,8),(8,0,4),(16,0,2),(32,0,0))
APA102[0] = apa_array[0]
APA102[1] = apa_array[1]
APA102[2] = apa_array[2]
APA102[3] = apa_array[3]
APA102[4] = apa_array[4]
APA102[5] = apa_array[5]

'''
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