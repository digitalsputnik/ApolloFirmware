import uasyncio as asyncio
import machine
import network
import time
import pysaver

connect_wifi_flag = asyncio.ThreadSafeFlag()
set_ap_flag = asyncio.ThreadSafeFlag()
mode_changed_flag = asyncio.ThreadSafeFlag()
get_status_flag = asyncio.ThreadSafeFlag()

is_ap = pysaver.load("is_ap")
device_id = pysaver.load("device_id")
    
async def setup():
    asyncio.create_task(toggle_network_mode_loop())
    asyncio.create_task(connect_loop())
    asyncio.create_task(set_ap_loop())
    asyncio.create_task(get_status_loop())
    if is_ap:
        await set_ap()
    else:
        await connect_to_smallest_apollo()
        
async def toggle_network_mode_loop():
    global is_ap
    while True:
        await mode_changed_flag.wait()
        is_ap = not is_ap
        #pysaver.save("is_ap", is_ap)
        #machine.reset()
        print("Network Mode Changed. Is ap - " + str(is_ap))
        
async def connect_loop():
    global is_ap
    while True:
        await connect_wifi_flag.wait()
        is_ap = False
        #pysaver.save("is_ap", is_ap)
        #machine.reset()
        print("Setting client. Is ap - " + str(is_ap))
        
async def set_ap_loop():
    global is_ap
    while True:
        await set_ap_flag.wait()
        is_ap = True
        #pysaver.save("is_ap", is_ap)
        #machine.reset()
        print("Setting ap. Is ap - " + str(is_ap))
        
async def get_status_loop():
    global is_ap
    while True:
        await get_status_flag.wait()
        print("Is ap - " + str(is_ap))

async def set_ap():
    global sta_if, device_id
    sta_if = network.WLAN(network.AP_IF)
    sta_if.active(True)
    sta_if.config(essid=device_id, authmode=network.AUTH_WPA_WPA2_PSK, password="dsputnik")

    print('\nnetwork config:', sta_if.ifconfig())

async def connect_to_smallest_apollo(callback=None):
    apollo_found = False
    while not apollo_found:
        ssids = scan_ssids()
        smallest_apollo = 9999
        for ssid in ssids:
            if b"Apollo" in ssid[0]:
                if smallest_apollo > int(ssid[0][-4:]):
                    smallest_apollo = int(ssid[0][-4:])
                    apollo_found = True

        if apollo_found:
            selected_ssid = "Apollo" + '{:0>{w}}'.format(str(smallest_apollo), w=4)
            connect(selected_ssid,"dsputnik")
        else:
            print("Apollo not found")
            await asyncio.sleep(5)

async def connect(ssid,pw,callback=None):
    global sta_if
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.connect(ap, passw)
        while not sta_if.isconnected():
            time.sleep(0.3)
            print(". ", end=" ")
    
    if callback != None:
        callback(sta_if.isconnected())
    print('\nnetwork config:', sta_if.ifconfig())

def scan_ssids():
    global sta_if
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    ssids = sta_if.scan()
    return ssids