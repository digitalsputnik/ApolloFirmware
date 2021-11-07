import network
import socket
import machine
import time
import Render
import ble_repl
import btree


# Define WiFi functionality
def wifiConnect(ap,passw):
    global sta_if
    sta_if = network.WLAN(network.STA_IF)

    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(ap, passw)
        # create timer task to check connection and repair any issues
        while not sta_if.isconnected():
            time.sleep(0.3)
            print(".", end=" ")

    print("")
    print('network config:', sta_if.ifconfig())

def wifiAp():
    global sta_if
    sta_if = network.WLAN(network.AP_IF)
    sta_if.active(True)
    sta_if.config(essid=deviceId, password="soomez")

    print("")
    print('network config:', sta_if.ifconfig())
    
    
def getDeviceId():
    x = input('Enter device id please: ')
    return x.encode('utf-8')

def getArtNetPreference():
    while True:
        x = input('Do you want to enable Artnet? (yes/no): ')
        if x.lower() == 'yes' or x.lower() == 'no':
            return x.encode('utf-8')

enableAll = machine.Pin(27, machine.Pin.OUT, value=0)
machine.Pin(21, machine.Pin.OUT, value=0)
machine.Pin(18, machine.Pin.OUT, value=0)
machine.Pin(19, machine.Pin.OUT, value=0)
machine.Pin(4, machine.Pin.OUT, value=0)

# open btree database
try:
    f = open("mydb", "r+b")
    db = btree.open(f)
except OSError:
    f = open("mydb", "w+b")
    db = btree.open(f)
    print('Database file not found, getting info...')
    db[b'Name'] = getDeviceId()
    db[b'ArtNet'] = getArtNetPreference()
    db.flush()
    


try:
    deviceId =  db[b"Name"]
except KeyError:
    db[b'Name'] = getDeviceId()
    deviceId =  db[b"Name"]

if not b'ArtNet' in db:
    db[b'ArtNet'] = getArtNetPreference()


#i2c
i2c = machine.SoftI2C(scl=machine.Pin(22), sda=machine.Pin(23))

# LED output RGBW
Output = Render.Render(i2cInterface=i2c)

# fan @ pin(0)
fan = machine.PWM(machine.Pin(0),duty=1023)

# Input Voltage sensor 1:7.81
inputVoltage = machine.ADC(machine.Pin(32))
inputVoltage.atten(machine.ADC.ATTN_11DB)

# prooviks vilksatuse vastu
time.sleep(2)
# enable outputs

enableAll = machine.Pin(27, machine.Pin.OUT, value=1)

# enable BLE'
ble_repl.start(deviceId)