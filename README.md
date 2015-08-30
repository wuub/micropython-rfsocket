# micropython-rfsocket
Micropython implementation of popular 433MHzn based RFSockets (i.e. Anslut/Proove/Nexa)

## Installation

  1. Get upip for your python3 installation `pip install micropython-upip`
  2. Create "lib" directory on your micropython SDcard/Filesystem
  3. Install micropython-rfsocket there like this `python -m upip install -p /media/[your-login]/45DE-XXXX/lib micropython-rfsocket`
  4. Use in `main.py` like this: `from rfsocket import RFSocket`


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

