# micropython-rfsocket
Micropython implementation of popular 433MHz based RF Sockets (i.e. Anslut/Proove/Nexa) using cheapo FS1000A transmitter. 

## Installation

  1. Get upip for your python3 installation `pip install micropython-upip`
  2. Create "lib" directory on your micropython SDcard/Filesystem
  3. Install micropython-rfsocket there like this `python -m upip install -p /media/[your-login]/45DE-XXXX/lib micropython-rfsocket`
  4. Use in `main.py` like this: `from rfsocket import RFSocket`

## Range
As far as I can tell FS100A transmitter connected to 3V3 seems to be at least twice as strong as the remote sold with the sockets. Stock remote is spotty at best. FS1000A was able to reliably toggle the socket trough multiple walls.  

## Basic usage

```python
#!/usr/bin/env python3

import pyb
from rfsocket import RFSocket

p = pyb.Pin('X1', pyb.Pin.OUT_PP)
r = RFSocket(p)

sw = pyb.Switch()
on_led = pyb.LED(2)
off_led = pyb.LED(1)

toggle = True
while True:
    if sw():
        if toggle:
            r.group_on()
            on_led.on()
            off_led.off()
        else:
            r.group_off()
            on_led.off()
            off_led.on()
        toggle = not toggle
        pyb.delay(300)
  ```

