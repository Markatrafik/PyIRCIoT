
For example, when you attach the ESP8266 to your Linux,
you can see something like this:

> dmesg | grep -e'tty' | tail -n1
[1234.5678] usb 3-8: cp210x converter now attached to ttyUSB1

OK, let's add this Chip to IRC-IoT ecosystem
> myport=/dev/ttyUSB1

1. Install required tools:
> pip3 install esptool mock adafruit-ampy
> apt-get install picocom # for Debian based Linux

2. Download MicroPython firmware, for example:
> myfw="esp8266-20191220-v1.12.bin"
or you can use this image to flash ESP32 module:
> myfw="esp32-idf3-20200415-v1.12.bin"
> wget http://micropython.org/resources/firmware/$myfw

3. Write MicroPython firmware to your ESP8266,
example for ESP8266 module (tested on ESP-01S and ESP-12E):
> esptool.py --port $myport erase_flash
> esptool.py --port $myport --baud 115200 write_flash \
>  --flash_size=detect 0 $myfw
example for ESP32 module (tested on ESP32-WROOM-32U):
> esptool.py --chip esp32 --port $myport --baud 115200 \
>  write_flash --flash_size=detect 0x1000 $myfw

4. Edit file main.py, to change your settings

5. Upload mini version of PyIRCIoT to your ESP8266:
> for i in rfc1459mini.py irciotmini.py main.py ; do
>  ampy -p $myport -b 115200 rm $i 2>/dev/null
>  ampy -p $myport -b 115200 put $i ; done
> ampy -p $myport -b 115200 ls
/boot.py
/irciotmini.py
/main.py
/rfc1459mini.py

6. You can debug source code by picocom utility
> picocom $myport -b115200
* Press the <Enter> key several times, type: help()
* and press the <Enter> again

7. Restart your ESP8266 and look to the IRC channel
* In picocom utility press Ctrl+D to soft restart
* or simply unplug and plug the dongle again

