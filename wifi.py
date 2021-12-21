import uasyncio as asyncio
import machine
import network
import pysaver
import flags
import apa_controller as apa

connected = False

is_ap = pysaver.load("is_ap", True)

if (is_ap[1]):
    is_ap = is_ap[0]
else:
    is_ap = True
    pysaver.save("is_ap", is_ap)

device_id = pysaver.load("device_id", True)

if (device_id[1]):
    device_id = device_id[0]
else:
    device_id = "ApolloXXXX"
    pysaver.save("device_id", device_id)
    
async def __setup__():
    update_apa()
    
    asyncio.create_task(toggle_network_mode_waiter())
    
    if is_ap:
        await set_ap()
    else:
        await connect_to_smallest_apollo(wifi_callback)
        # await connect("Apollo0000", "dsputnik", wifi_callback)

async def __slowerloop__():
    update_apa()
    
async def toggle_network_mode_waiter():
    global is_ap
    while True:
        await flags.program_long_flag.wait()
        is_ap = not is_ap
        update_apa()
        pysaver.save("is_ap", is_ap)
        machine.reset()
        print("Network Mode Changed. Is ap - " + str(is_ap))

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
            connect(selected_ssid,"dsputnik", callback)
            print("Connected to " + str(selected_ssid))
        else:
            print("Apollo not found")
            await asyncio.sleep(5)

async def connect(ssid,pw,callback=None):
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

def wifi_callback(status):
    global connected
    connected = status
    
def scan_ssids():
    global sta_if
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    ssids = sta_if.scan()
    return ssids

def update_apa():
    global is_ap, connected
    if is_ap:
        for i in range(6):
            apa.set_led(i,(0,0,int(i*30)))
    else:
        if connected:
            for i in range(6):
                apa.set_led(i,(int(i*30),0,0))
        else:
            for i in range(6):
                apa.set_led(i,(0,int(i*30),0))