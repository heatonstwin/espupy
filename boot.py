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
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            if time.ticks_diff(time.ticks_ms(), start) > 30000:
                print('failed to connect to {}'.format(ssid))
                break
    print('network config:', wlan.ifconfig())


#ap = network.WLAN(network.AP_IF) # create access-point interface
#ap.active(True)         # activate the interface
#ap.config(essid='ESP-AP') # set the ESSID of the access point

gc.collect()