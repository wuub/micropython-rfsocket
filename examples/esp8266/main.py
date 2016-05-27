from machine import freq
freq(160000000)  # unfortuneately, on lower settings it's almost unusable
del freq

from machine import Pin
from rfsocket import RFSocket, Esp8266Timings


pin = Pin(0, Pin.OUT)
sock = RFSocket(pin, RFSocket.ANSLUT, timings=Esp8266Timings)
