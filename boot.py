import esp
esp.osdebug(None)

import gc
import network
import time
import webrepl

webrepl.start()
wlan = network.WLAN(network.STA_IF)
wlan.active(True)


def do_connect(ssid, password):
    start = time.ticks_ms()
    if wlan.isconnected():
        print('disconnecting from network...')
        wlan.disconnect()
    print('connecting to network...')
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        if time.ticks_diff(time.ticks_ms(), start) > 30000:
            print('failed to connect to {}'.format(ssid))
            break
    print('network config:', wlan.ifconfig())


def wifi_scan():
    scan = sorted(wlan.scan(), key=lambda x: x[3], reverse=True)
    for essid, bssid, channel, rssi, authmode, hidden in scan:
        print('essid={} dB={}'.format(essid.decode(), rssi))


gc.collect()
