import machine
import pysaver
import Data.pins as pins

TYPE_APA = 0
TYPE_NEO = 1

led_count = 6

led_type = pysaver.load("led_type", TYPE_APA, True)

apa_sck_pin = pins.apa_sck_pin
apa_mosi_pin = pins.apa_mosi_pin
apa_miso_pin = pins.apa_miso_pin

neopixel_pin = pins.neopixel_pin

if (led_type == TYPE_APA):
    from Lib.micropython_dotstar import DotStar as apa102
    spi = machine.SoftSPI(sck=machine.Pin(apa_sck_pin), mosi=machine.Pin(apa_mosi_pin), miso=machine.Pin(apa_miso_pin))
    leds = apa102(spi,led_count)
else:
    import neopixel
    leds = neopixel.NeoPixel(machine.Pin(neopixel_pin), led_count)

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
    global led_type, leds, locked_leds, TYPE_NEO
    if (led not in locked_leds):
        leds[led] = color
        if (led_type == TYPE_NEO):
            leds.write()