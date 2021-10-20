from machine import Pin, I2C
from math import floor
from time import sleep

class LM75(object):
    _address = 0x4f

    def __init__(self, i2cInput, address=0x4f):
        self.i2c = i2cInput
        self._address = address

    def get_output(self):
        """Return raw output from the LM75 sensor."""
        output = self.i2c.readfrom(self._address, 2)
        return output[0], output[1]

    def get_temp(self):
        """Return a tuple of (temp_c, point)."""
        temp = self.get_output()
        return int(temp[0]), floor(int(temp[1]) / 23)
