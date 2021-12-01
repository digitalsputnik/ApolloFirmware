from math import floor
import time
import machine

class E_uLM75(object):
    _address = 0x4f
    _error = "None"
    _last_results = (0,0)
    _last_read = 0
    _current_temp = 0
    _temp_values = []

    def __init__(self, i2cInput, address=0x4f):
        self.i2c = i2cInput
        self._address = address
        
        self._tempTimer = machine.Timer(2)
        #Update the value 1Hz, once 6 reading are preformed the geomtric midlle is returnes as curren_temp
        self._tempTimer.init(period=1000, mode=machine.Timer.PERIODIC, callback=self._updateTemp) 

    def _get_output(self):
        """Return raw output from the LM75 sensor."""
        output = self.i2c.readfrom(self._address, 2)
        return output[0], output[1]

    def _get_temp(self):
        """Return a int, the temp in Celsius x 10"""
        try:
            temp = self._get_output()
            self._last_results = (int(temp[0]), floor(int(temp[1]) / 23))
            return int(self._last_results[0]*10+self._last_results[1])
        except Exception as e:
            self._error = E
            time.sleep(0.01)
            return 220 # Average room temperature is 22 degrees celcius
        
    def _updateTemp(self,caller):
        if len(self._temp_values) < 7:
            self._temp_values.append(self._get_temp())
        else:
            self._current_temp = self._temp_values[3]
            self._temp_values = []
            
    def read(self):
        return self._current_temp
            
        
