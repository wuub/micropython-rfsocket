#!/usr/bin/env python3

import machine
import utime

def default_remote_id():
    """generate remote id based on machine.unique_id()"""
    import uhashlib
    from ustruct import unpack
    # we compute a hash of board's unique_id, since a boards manufactured
    # closely together probably share prefix or suffix, and I don't know
    # which one. we want to avoid accidental remote_id clashes
    unique_hash = uhashlib.sha256(machine.unique_id()).digest()
    # and a 4 byte prefix of a sha256 hash is more than enough
    uint32 = unpack("I", unique_hash[:4])[0]
    # let's mask it to 26 bits
    uint26 = uint32 & (2**26 - 1)
    return uint26

def payload(remote_id, group, toggle, chan, unit):
    """generate binary payload from given values"""
    return (remote_id << 6) | (group << 5) | (toggle << 4) | (chan << 2) | unit


class RFTimings:
    # timings
    T = 250         # base delay of 250 us/microseconds
    ONE = T         #  ^_
    ZERO = 5 * T    #  ^_____
    START = 10 * T  #  ^__________
    STOP = 40 * T   #  ^________________________________________
    RETRIES = 5     # number of times, each message is sent


class Esp8266Timings(RFTimings):
    T = 210
    ONE = 130
    RETRIES = 7


class RFSocket:
    """
    Control popular 433MHz RF sockets.

    >>> p = Pin('X1', Pin.OUT_PP)
    >>> r = RFSocket(p, RFSocket.ANSLUT)
    >>> r.on(1)  # or 2 or 3
    >>> r.off(1)
    >>> r.group_on()
    >>> r.group_off()

    By default each micropython board will have a unique remote_id
    generated from machine.unique_id().
    """

    # group values
    GROUP = 0  # control a whole group
    DEVICE = 1  # control a single device

    # toggle values
    ON = 0   # [sic!] turn ON a DEVICE or GROUP
    OFF = 1  # [sic!] turn OFF a DEVICE or GROUP

    # chann values
    ANSLUT = 0b00
    NEXA = 0b11

    # unit values
    UNITS = {
        ANSLUT: {1: 0b00, 2: 0b01, 3: 0b10},
        NEXA: {1: 0b11, 2: 0b10, 3: 0b01},
    }

    def __init__(self, pin, chann=ANSLUT, remote_id=0, timings=RFTimings):
        self._pin = pin
        self._chann = chann
        self._remote_id = (remote_id & (2**26 - 1)) or default_remote_id()
        self._timings = timings
        self._status = [False, False, False]

    def group_on(self):
        """Turn on all the devices."""
        bits = payload(self._remote_id, self.GROUP, self.ON, self._chann, 0)
        self._send(bits)
        for i in range(3):
            self._status[i] = True

    def group_off(self):
        """Turn off all the devices."""
        bits = payload(self._remote_id, self.GROUP, self.OFF, self._chann, 0)
        self._send(bits)
        for i in range(3):
            self._status[i] = False

    def on(self, unit):
        bits = payload(self._remote_id, self.DEVICE, self.ON, self._chann, self.UNITS[self._chann][unit])
        self._send(bits)
        self._status[unit - 1] = True

    def off(self, unit):
        bits = payload(self._remote_id, self.DEVICE, self.OFF, self._chann, self.UNITS[self._chann][unit])
        self._send(bits)
        self._status[unit - 1] = False

    def status(self):
        return tuple(self._status)

    @staticmethod
    def _phys(t, m, high, low, udelay=utime.sleep_us):
        """
        Send one physical 'bit' of information, either ONE, ZERO, START or STOP.

        Using high, low and udelay locals for performance and better timing.
        """
        high()
        udelay(t)
        low()
        udelay(m)

    def _send(self, msg):
        """Send msg to the transmitter, repeat it appropriate number of times."""
        for _ in range(self._timings.RETRIES):
            self._send_one(msg)

    def _send_one(self, msg):
        """Send a single 32bit message."""
        # bring some of the stuff as local variables, this greately
        # improves/stabilizes message signal timings
        t, one, zero, start, stop = self._timings.T, self._timings.ONE, self._timings.ZERO, self._timings.START, self._timings.STOP
        high = self._pin.high
        low = self._pin.low
        _phys = self._phys

        mask = 1 << 31
        _phys(t, start, high, low)
        for _ in range(32):
            if mask & msg:
                # logical one is encoded as physical ONE followed by physical ZERO
                _phys(t, one, high, low)
                _phys(t, zero, high, low)
            else:
                # logical zero is encoded as physical ZERO followed by physical ONE
                _phys(t, zero, high, low)
                _phys(t, one, high, low)
            msg = msg << 1  # next bit
        _phys(t, stop, high, low)
