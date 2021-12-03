import network
import socket
import machine
import time
import ble_repl
import btree

# disable all outputs to avoid blinking during setup 
machine.Pin(27, machine.Pin.OUT, value=0)


# open btree database
try:
    f = open("mydb", "r+b")
except OSError:
    f = open("mydb", "w+b")

db = btree.open(f)

deviceId =  db[b"Name"]

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


# Input Voltage sensor 1:7.81
inputVoltage = machine.ADC(machine.Pin(32))
inputVoltage.atten(machine.ADC.ATTN_11DB)

# enable BLE
ble_repl.start(deviceId)