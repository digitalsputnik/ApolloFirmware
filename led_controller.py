import machine
import pysaver
import Data.pins as pins

# Led type constants
TYPE_APA = 0
TYPE_NEO = 1

# Number of leds on the strip
_led_count = 6

# Loading saved led type
_led_type = pysaver.load("led_type", TYPE_APA, True)

# Pin assignments
_apa_sck_pin = pins.apa_sck_pin
_apa_mosi_pin = pins.apa_mosi_pin
_apa_miso_pin = pins.apa_miso_pin

_neopixel_pin = pins.neopixel_pin

# Import correct module based on led type
if (_led_type == TYPE_APA):
    from Lib.micropython_dotstar import DotStar as apa102
    _spi = machine.SoftSPI(sck=machine.Pin(_apa_sck_pin), mosi=machine.Pin(_apa_mosi_pin), miso=machine.Pin(_apa_miso_pin))
    _leds = apa102(_spi,_led_count)
else:
    import neopixel
    _leds = neopixel.NeoPixel(machine.Pin(_neopixel_pin), _led_count)

_locked_leds = []

# Lock some led indexes to avoid overwriting them from other instances
# This is used to create gradients on the led strip without having to know which led not to overwrite
def lock_led(_led):
    global _locked_leds
    if (_led not in _locked_leds):
        _locked_leds.append(_led)

# Unlock previously locked leds
def unlock_led(_led):
    global _locked_leds
    if (_led in _locked_leds):
        _locked_leds.remove(_led)

def unlock_all_leds():
    global _locked_leds
    _locked_leds = []

# Set the color of a led, _led is the index of the led
def set_led(_led, _color):
    global _led_type, _leds, _locked_leds, TYPE_NEO
    # Check if led is locked
    if (_led not in _locked_leds):
        _leds[_led] = _color
        # Neopixel leds require .write() to apply color to the leds, APA leds don't
        if (_led_type == TYPE_NEO):
            _leds.write()