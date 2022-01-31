import uasyncio as asyncio
import machine
import network
import pysaver
import flags
import time
import led_controller as led

connected = False
network_mode_waiter_task = None

update_leds = True

AP = 0
CLIENT = 1

network_mode = pysaver.load("network_mode", AP, True)

wifi_ssid = pysaver.load("wifi_ssid", None)
wifi_pw = pysaver.load("wifi_pw", None)

device_id = pysaver.load("device_id", "ApolloXXXX", True)
    
async def __setup__():
    global network_mode_waiter_task, network_mode, AP, CLIENT, wifi_ssid, wifi_pw
    
    network_mode_waiter_task = asyncio.create_task(toggle_network_mode_waiter())
    
    if network_mode is CLIENT:
        update_led()
        await set_client()
    else:
        update_led()
        await set_ap()

async def __slowerloop__():
    global connected, sta_if
    try:
        new_connected_value = sta_if.isconnected()
        if connected is not new_connected_value and network_mode is not AP:
            connected = new_connected_value
            update_led()
    except:
        pass
    
async def toggle_network_mode_waiter():
    global network_mode, AP, CLIENT, wifi_ssid, wifi_pw
    while True:
        await flags.program_long_flag.wait()
        led.on = False
        led.apply_color()
        network_mode = network_mode + 1
        if network_mode > 1:
            network_mode = 0
        pysaver.save("network_mode", network_mode)
        machine.reset()
        print("Network Mode Changed. Network Mode - " + str(network_mode))

async def set_ap():
    global sta_if, device_id
    sta_if = network.WLAN(network.AP_IF)
    sta_if.active(True)
    sta_if.config(essid=device_id, authmode=network.AUTH_WPA_WPA2_PSK, password="dsputnik")
    print('\nNetwork config: '+str(sta_if.ifconfig()))

async def set_client():
    global wifi_ssid, wifi_pw, connected
    if wifi_ssid is not None:
        while connected is False:
            print("Trying custom client")
            await start_connecting(wifi_ssid, wifi_pw)
            connected = sta_if.isconnected()
            if connected is False:
                print("Trying closest apollo")
                await connect_to_smallest_apollo()
    else:
        while connected is False:
            await connect_to_smallest_apollo()
            print("Trying again")

async def connect_to_smallest_apollo(callback=None, timeout_ms=10000):
    apollo_found = False
    timed_out = False
    start_time = time.ticks_ms()
    while not apollo_found and not timed_out:
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
            await asyncio.sleep(2)
            
        if (time.ticks_ms() - start_time) > timeout_ms:
            timed_out = True
            print("Closest Apollo Timed Out")

async def start_connecting(ssid, pw, callback=None, timeout_ms=10000):
    global sta_if
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('Connecting to network...')
        sta_if.active(True)
        sta_if.connect(ssid, pw)
        timed_out = False
        start_time = time.ticks_ms()
        while not sta_if.isconnected() and not timed_out:
            if (time.ticks_ms() - start_time) > timeout_ms:
                timed_out = True
                sta_if.active(False)
                print("\nClient timed out")
            await asyncio.sleep_ms(500)
            print(".", end=" ")
    
    if callback != None:
        callback(connected)
        
    if connected:
        print('\nNetwork config:', sta_if.ifconfig())
    
def change_network_mode(mode = 0, ssid="", pw=""):
    global network_mode, CLIENT, wifi_ssid, wifi_pw
    
    network_mode = mode
    pysaver.save("network_mode", network_mode)
    
    if mode is CLIENT:
        #change the SSID and PW only if they are provided otherwise keep the saved values
        if ssid != "":
            wifi_ssid = ssid
        if pw != "":
            wifi_pw = pw
        pysaver.save("wifi_ssid", wifi_ssid)
        pysaver.save("wifi_pw", wifi_pw)
        
    machine.reset()

def delete_saved_ssid():
    pysaver.delete("wifi_ssid")
    pysaver.delete("wifi_pw")
    
def scan_ssids():
    global sta_if
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    ssids = sta_if.scan()
    return ssids

def update_led():
    global connected, network_mode, AP, sta_if, wifi_ssid
    
    if update_leds:
        _blue_gradient = [[0, 0, 40], [0, 0, 80], [0, 0 ,120], [0, 0, 160], [0, 0, 200], [0, 0, 240]]
        _yellow_gradient = [[40, 40, 0], [80, 80, 0], [120, 120 ,0], [160, 160, 0], [200, 200, 0], [240, 240, 0]]
        _red_gradient = [[40, 0, 0], [80, 0, 0], [120, 0 ,0], [160, 0, 0], [200, 0, 0], [240, 0, 0]]
        _green_gradient = [[0, 40, 0], [0, 80, 0], [0, 120 ,0], [0, 160, 0], [0, 200, 0], [0, 240, 0]]
    
        if network_mode is AP:
            led.set_custom_pattern(led.BACKGROUND_LAYER, _blue_gradient)
        else:
            if connected:
                if sta_if.config('essid') is wifi_ssid:
                    led.set_custom_pattern(led.BACKGROUND_LAYER, _green_gradient)
                else:
                    led.set_custom_pattern(led.BACKGROUND_LAYER, _yellow_gradient)
            else:
                led.set_custom_pattern(led.BACKGROUND_LAYER, _red_gradient)