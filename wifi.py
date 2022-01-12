import uasyncio as asyncio
import machine
import network
import pysaver
import flags
import led_controller as led

connected = False
network_mode_waiter_task = None

AP = 0
APOLLO_CLIENT = 1
CLIENT = 2

network_mode = pysaver.load("network_mode", AP, True)

wifi_ssid = pysaver.load("wifi_ssid", None)
wifi_pw = pysaver.load("wifi_pw", None)

device_id = pysaver.load("device_id", "ApolloXXXX", True)
    
async def __setup__():
    global network_mode_waiter_task, network_mode, AP, CLIENT, APOLLO_CLIENT, wifi_ssid, wifi_pw
    update_led()
    
    network_mode_waiter_task = asyncio.create_task(toggle_network_mode_waiter())
    
    if network_mode is AP:
        await set_ap()
    elif network_mode is APOLLO_CLIENT:
        await connect_to_smallest_apollo()
    elif network_mode is CLIENT and wifi_ssid is not None:
        await start_connecting(wifi_ssid, wifi_pw)
    else:
        print("Ssid not set, setting AP")
        await set_ap()

async def __slowerloop__():
    global connected, sta_if
    connected = sta_if.isconnected()
    update_led()
    
async def toggle_network_mode_waiter():
    global network_mode, AP, CLIENT, APOLLO_CLIENT, wifi_ssid, wifi_pw
    while True:
        await flags.program_long_flag.wait()
        if wifi_ssid is None:
            network_mode = network_mode + 1
            if network_mode > 1:
                network_mode = 0
        else:
            network_mode = network_mode + 1
            if network_mode > 2:
                network_mode = 0
        update_led()
        pysaver.save("network_mode", network_mode)
        machine.reset()
        print("Network Mode Changed. Network Mode - " + str(network_mode))

async def set_ap():
    global sta_if, device_id
    sta_if = network.WLAN(network.AP_IF)
    sta_if.active(True)
    sta_if.config(essid=device_id, authmode=network.AUTH_WPA_WPA2_PSK, password="dsputnik")

    print('\nNetwork config:', sta_if.ifconfig())

async def connect_to_smallest_apollo(callback=None):
    apollo_found = False
    while not apollo_found:
        ssids = scan_ssids()
        smallest_apollo = 9999
        for ssid in ssids:
            if b"Apollo" in ssid[0] and len(ssid[0]) == 10:
                if smallest_apollo > int(ssid[0][-4:]):
                    smallest_apollo = int(ssid[0][-4:])
                    apollo_found = True

        if apollo_found:
            selected_ssid = "Apollo" + '{:0>{w}}'.format(str(smallest_apollo), w=4)
            print("Apollo found - " + str(selected_ssid))
            await start_connecting(selected_ssid,"dsputnik", callback)
        else:
            print("Apollo not found")
            await asyncio.sleep(5)
            
def connect(ssid, pw):
    global sta_if, connected, network_mode, AP, CLIENT, APOLLO_CLIENT, wifi_ssid, wifi_pw
    network_mode = CLIENT
    wifi_ssid = ssid
    wifi_pw = pw
    update_led()
    pysaver.save("network_mode", network_mode)
    pysaver.save("wifi_ssid", wifi_ssid)
    pysaver.save("wifi_pw", wifi_pw)
    machine.reset()

def delete_saved_ssid():
    pysaver.delete("wifi_ssid")
    pysaver.delete("wifi_pw")

async def start_connecting(ssid,pw,callback=None):
    global sta_if
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('Connecting to network...')
        sta_if.active(True)
        sta_if.connect(ssid, pw)
        while not sta_if.isconnected():
            await asyncio.sleep_ms(500)
            print(".", end=" ")
    
    if callback != None:
        callback(sta_if.isconnected())
    print('\nNetwork config:', sta_if.ifconfig())
    
def scan_ssids():
    global sta_if
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    ssids = sta_if.scan()
    return ssids

def update_led():
    global connected, network_mode, AP
    if network_mode is AP:
        for i in range(6):
            led.set_led(i,(0,0,int(i*30)))
    else:
        if connected:
            for i in range(6):
                led.set_led(i,(int(i*30),0,0))
        else:
            for i in range(6):
                led.set_led(i,(0,int(i*30),0))