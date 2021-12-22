from Lib.micropython_dotstar import DotStar as apa102
import machine
import pysaver

led_count = 6

apa_sck_pin = pysaver.load("apa_sck_pin", 26, True)
apa_mosi_pin = pysaver.load("apa_mosi_pin", 25, True)
apa_miso_pin = pysaver.load("apa_miso_pin", 0, True)

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