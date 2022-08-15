# Everything in this file will be ran before lamp setup functions and main loops are started
# If program button is held down during boot. The script will be ignored

# TODO - investigate why loading this script slows boot time

import artnet_client

# Were executing this logic as a string in artnet_client to have this the property as alocal variable in the context of the artnet_repl
property_logic = """class Property:
    
    def __init__(self, name, value, _oe = "", _oc = "", _ou = "", _oca = ""):
        self.name = name
        self._value = value
        self._on_edit = _oe
        self._on_create = _oc
        self._on_update = _ou
        self._on_cancel = _oca
        
    def set_value(self, value):
        self._value = value
        exec(self._on_edit)
        
    def get_value(self):
        return self._value

properties = []

color = Property('color', [0,0,0,0,0], 'renderer.set_color(color.get_value()[0], color.get_value()[1], color.get_value()[2], color.get_value()[3], color.get_value()[4])')
"""

artnet_client.execute_command(property_logic)