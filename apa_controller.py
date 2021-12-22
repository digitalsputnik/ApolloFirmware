from Lib.micropython_dotstar import DotStar as apa102
import machine
import pysaver
import Data.pins as pins

led_count = 6

apa_sck_pin = pins.apa_sck_pin
apa_mosi_pin = pins.apa_mosi_pin
apa_miso_pin = pins.apa_miso_pin

spi = machine.SoftSPI(sck=machine.Pin(apa_sck_pin), mosi=machine.Pin(apa_mosi_pin), miso=machine.Pin(apa_miso_pin))
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