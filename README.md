# ApolloFirmware
Micropython software for the Apollo lamps


# instalation

1. Download micropython: https://micropython.org/download/esp32/ (1.17 with spi RAM)
1. Install Pyrhon3, pip3
1. Install ampy (```pip3 install adafruit-ampy```)
1. Install esptool (```pip3 install esptool```)
1. Install micropython to the board
  * ```esptool.py --port **COM port** erase_flash```
  * ```esptool.py --chip esp32 --port **COM port** write_flash -z 0x1000 **filename.bin**```
6. Upload all files ```ampy -p **COM port** put ./*```


# terminal usage
Both serial and BLE terminal are supported
1. Connect (```screen **COM port** 115200```)
2. Set color 8bit values (0-255) (```Output.setColor(255,255,255)```)
3. Set uncalibrated color 10bit values (0-1023)  (```Output.pushRGBW((1023,1023,1023,1023))```)
4. Get temperature of the led board (```Output._currentTemp```)
