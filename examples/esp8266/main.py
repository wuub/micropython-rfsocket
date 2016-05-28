#!/usr/bin/env python3
import usocket
from machine import Pin, freq, reset
from rfsocket import Esp8266Timings, RFSocket
from webrepl import start

freq(160000000)  # unfortuneately, on lower settings it's almost unusable
start()
rf_pin = Pin(0, Pin.OUT)


REMOTES = {}


def remote(remote_id_str):
    remote_id = int(remote_id_str)
    if remote_id not in REMOTES:
        REMOTES[remote_id] = RFSocket(rf_pin, RFSocket.ANSLUT, timings=Esp8266Timings)
    return REMOTES[remote_id]


def switch_on(remote_id_str, switch_num_str):
    switch_num = int(switch_num_str)
    r = remote(remote_id_str)
    r.on(switch_num)
    return r.status()


def switch_off(remote_id_str, switch_num_str):
    switch_num = int(switch_num_str)
    r = remote(remote_id_str)
    r.off(switch_num)
    return r.status()


def group_on(remote_id_str):
    r = remote(remote_id_str)
    r.group_on()
    return r.status()


def group_off(remote_id_str):
    r = remote(remote_id_str)
    r.group_off()
    return r.status()


def remote_status(remote_id_str):
    r = remote(remote_id_str)
    return r.status()


def remotes():
    return REMOTES.keys()


COMMANDS = {
    "switch_on": switch_on,
    "switch_off": switch_off,
    "group_on": group_on,
    "group_off": group_off,
    "remotes": remotes,
    "remote_status": remote_status,
}


def handle(sock):
    while True:
        line = sock.readline()
        if not line:
            break
        cmd, *args = line.strip().decode("utf-8").split()
        command = COMMANDS.get(cmd.lower())
        if not command:
            sock.sendall("ERR CommandNotFound\r\n")
            continue

        try:
            result = command(*args)
        except Exception as e:
            sock.sendall("ERR " + str(e) + "\r\n")
            continue
        sock.sendall("OK")
        for res in result:
            sock.send(" ")
            sock.sendall(str(res))
        sock.sendall("\r\n")


def main():
    server = usocket.socket(usocket.AF_INET, usocket.SOCK_STREAM)
    server.bind(("0.0.0.0", 1080))
    server.listen(3)

    while True:
        sock, addr = server.accept()
        print("Accepted", addr)
        handle(sock)
        print("Closing", addr)
        sock.close()


if __name__ == '__main__':
    main()
