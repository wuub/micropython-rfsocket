
import pyb


class RFSocket:
    """Control popular RF sockets"""

    # timings
    T = 250         # base delay of 250 us/microseconds
    ONE = T         #  ^_
    ZERO = 5 * T    #  ^_____
    START = 10 * T  #  ^__________
    STOP = 40 * T   #  ^________________________________________
    RETRIES = 5     # number of times, each message is sent

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


    def __init__(self, pin, remote_id, chann):
        self._pin = pin
        self._remote_id = remote_id
        self._chann = chann


    def group_on(self):
        """turn on all the devices"""
        payload = self._payload(self.GROUP, self.ON, self._chann, 0)
        self._send(payload)

    def group_off(self):
        """turn off all the devices"""
        payload = self._payload(self.GROUP, self.OFF, self._chann, 0)
        self._send(payload)

    def on(self, unit):
        payload = self._payload(self.DEVICE, self.ON, self._chann, self.UNITS[self._chann][unit])
        self._send(payload)

    def off(self, unit):
        payload = self._payload(self.DEVICE, self.OFF, self._chann, self.UNITS[self._chann][unit])
        self._send(payload)

    def _payload(self, group, toggle, chan, unit):
        return (self._remote_id << 6) | (group << 5) | (toggle << 4) | (chan << 2) | unit

    @staticmethod
    def _phys(t, m, high, low, udelay=pyb.udelay):
        """send one physical 'bit' of information, either ONE, ZERO, START or STOP
           using high, low and udelay locals for performance and better timing"""
        high()
        udelay(t)
        low()
        udelay(m)

    def _send(self, msg):
        """send msg to the transmitter, repeat it appropriate number of times"""
        for _ in range(self.RETRIES):
            self._send_one(msg)

    def _send_one(self, msg):
        """send a single 32bit message"""

        # bring some of the stuff as local variables, this greately
        # improves/stabilizes message signal timings
        t, one, zero, start, stop = self.T, self.ONE, self.ZERO, self.START, self.STOP
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
