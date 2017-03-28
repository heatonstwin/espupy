import time
import machine
import network
import ubinascii

import webserver


def pretty_mac():
    return ubinascii.hexlify(network.WLAN().config('mac')).decode()


def do_connect(ssid, password):
    error = False
    start = time.ticks_ms()
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if wlan.isconnected():
        print('disconnecting from network...')
        wlan.disconnect()
    print('connecting to network...')
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        if time.ticks_diff(time.ticks_ms(), start) > 30000:
            error = True
            break

    if error is True:
        machine.reset()

    print('network config:', wlan.ifconfig())


def wifi_scan():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    scan = sorted(wlan.scan(), key=lambda x: x[3], reverse=True)
    for essid, bssid, channel, rssi, authmode, hidden in scan:
        print('essid={} dB={}'.format(essid.decode(), rssi))


def get_config():
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(True)

    mac = pretty_mac()[-6:]
    essid = 'minibox-{}'.format(mac)
    password = 'senseit0'
    ap_if.config(essid=essid,
                 password=password,
                 hidden=False)

    print('essid={} password={}'.format(essid, password))
    print(ap_if.ifconfig())
    # Block until someone sets config
    webserver.serve()

    # Turn off the AP since we should be able to connect the the local WiFi
    ap_if.active(False)

    # Reboot to read in the config
    machine.reset()
