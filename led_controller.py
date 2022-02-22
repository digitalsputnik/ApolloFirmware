import machine
import pysaver
import Data.pins as pins

on = True

FOREGROUND_LAYER = 0
BACKGROUND_LAYER = 1

TYPE_APA = 0
TYPE_NEO = 1

led_count = 6

boot_pattern = [[255,0,255], [255,0,255], [255,0,255], [255,0,255], [255,0,255], [255,0,255]]
off_pattern = [[0, 0, 0], [0, 0, 0], [255, 0, 0], [255, 0, 0], [0, 0, 0], [0, 0, 0]]

foreground = []
background = boot_pattern

led_type = pysaver.load("led_type", TYPE_APA, True)

apa_sck_pin = pins.apa_sck_pin
apa_mosi_pin = pins.apa_mosi_pin
apa_miso_pin = pins.apa_miso_pin

neopixel_pin = pins.neopixel_pin

async def __setup__():
    global leds, foreground, background
    
    for i in range(led_count):
        foreground.append([0,0,0])
    
    if (led_type == TYPE_APA):
        from Lib.micropython_dotstar import DotStar as apa102
        spi = machine.SoftSPI(sck=machine.Pin(apa_sck_pin), mosi=machine.Pin(apa_mosi_pin), miso=machine.Pin(apa_miso_pin))
        leds = apa102(spi,led_count)
    else:
        import neopixel
        leds = neopixel.NeoPixel(machine.Pin(neopixel_pin), led_count)
        
    apply_color()

async def __slowerloop__():
    apply_color()

def apply_color():
    global leds, foreground, background
    if on:
        for j in range(led_count):
            #invert the output array
            i = led_count-j-1
            
            red = None
            green = None
            blue = None
        
            if (foreground[i] != [0,0,0]):
                red = foreground[i][0]
                green = foreground[i][1]
                blue = foreground[i][2]
            else:
                red = background[i][0]
                green = background[i][1]
                blue = background[i][2]
            
            leds[j] = (green, red, blue)
            if (led_type == TYPE_NEO):
                leds.write()
    else:
        for j in range(led_count):
            #invert the output array
            i = led_count-j-1
            
            red = off_pattern[i][0]
            green = off_pattern[i][1]
            blue = off_pattern[i][2]
            
            leds[j] = (green, red, blue)
            if (led_type == TYPE_NEO):
                leds.write()
                
def set_custom_pattern(layer, pattern):
    global foreground, background
    if layer is FOREGROUND_LAYER:
        foreground = pattern
    else:
        background = pattern

def set_solid_color(layer, color):
    global foreground, background
    if layer is FOREGROUND_LAYER:
        for i in range(led_count):
            foreground[i] = list(color)
    else:
        for i in range(led_count):
            background[i] = list(color)

def set_single_led(index, layer, color):
    global foreground, background
    if layer is FOREGROUND_LAYER:
        foreground[index] = list(color)
    else:
        background[index] = list(color)

def clear_foreground():
    global foreground
    for i in range(led_count):
        foreground[i] = [0,0,0]
        
def clear_background():
    global background
    for i in range(led_count):
        background[i] = [0,0,0]