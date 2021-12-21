from Lib.micropython_dotstar import DotStar as apa102
import machine

led_count = 6

sck_pin = 26
mosi_pin = 25
miso_pin = 0

spi = machine.SoftSPI(sck=machine.Pin(sck_pin), mosi=machine.Pin(mosi_pin), miso=machine.Pin(miso_pin))
apa = apa102(spi,led_count)

locked_leds = []

def lock_led(led):
    global locked_leds
    if (led not in locked_leds):
        locked_leds.append(led)

def unlock_led(led):
    global locked_leds
    if (led in locked_leds):
        locked_leds.remove(led)

def unlock_all_leds():
    global locked_leds
    locked_leds = []

def set_led(led, color):
    global apa, locked_leds
    if (led not in locked_leds):
        apa[led] = color