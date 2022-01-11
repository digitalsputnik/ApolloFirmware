# ApolloFirmware
Micropython software for the Apollo lamps


# instalation

1. Download micropython: https://micropython.org/download/esp32spiram/ (1.17)
1. Install Thonny: https://thonny.org/
2. Connect Apollo via USB Serial converter to the computer (need mac instructions for the yellow USBC board)
3. Install micropython to the ESP
   -> Run -> Select Interpeter -> MicroPython(ESP32)
   -> Lower left side there is an option to "install or update firmware", just above the OK button
   -> select "From image file(keep)"
   -> select "Erase flash before installing
6. Once the system is booted connect from thonny again, delete all files on flash
7. Uplad all files from the .py files and folders
8. Update the "Data/_device_id.py"
9. Update the "Data/pins.py


# terminal usage
Currently our own communication protocol is used in async mode
### Use Python to connect to the lamp
1. Download the DSDMpy (https://github.com/digitalsputnik/DSDM)
2. Connect to the same network as the lamp
### Use Blender to connect to the lamp
1. Download the python scene file ()
2. Connect to the same network as the lamp
3. Select the function You would like to preform from top center dropdown of py files. Dont use directly the files that sart with _
