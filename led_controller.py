import machine
import pysaver
import Data.pins as pins

FOREGROUND_LAYER = 0
BACKGROUND_LAYER = 1

TYPE_APA = 0
TYPE_NEO = 1

led_count = 6

starting_foreground = [0,0,0]
starting_background = [255,255,255]

foreground = []
background = []

led_type = pysaver.load("led_type", TYPE_APA, True)

apa_sck_pin = pins.apa_sck_pin
apa_mosi_pin = pins.apa_mosi_pin
apa_miso_pin = pins.apa_miso_pin

neopixel_pin = pins.neopixel_pin

async def __setup__():
    global leds, foreground, background
    
    for i in range(led_count):
        foreground.append(starting_foreground)
        background.append(starting_background)
    
    if (led_type == TYPE_APA):
        from Lib.micropython_dotstar import DotStar as apa102
        spi = machine.SoftSPI(sck=machine.Pin(apa_sck_pin), mosi=machine.Pin(apa_mosi_pin), miso=machine.Pin(apa_miso_pin))
        leds = apa102(spi,led_count)
    else:
        import neopixel
        leds = neopixel.NeoPixel(machine.Pin(neopixel_pin), led_count)

async def __slowerloop__():
    global leds, foreground, background
    for i in range(led_count):
        red = None
        green = None
        blue = None
        
        if (foreground[i] is not [0,0,0]):
            red = foreground[i][0]
            green = foreground[i][1]
            blue = foreground[i][2]
        else:
            red = background[i][0]
            green = background[i][1]
            blue = background[i][2]
        
        leds[i] = (green, red, blue)
        if (led_type == TYPE_NEO):
            leds.write()
            
def set_solid_color(layer, color):
    global foreground, background
    if layer is FOREGROUND_LAYER:
        foreground = list(color)
    else:
        background = list(color)