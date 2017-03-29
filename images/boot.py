import os

import esp

import config
from utilities import do_connect, get_config

esp.osdebug(None)

import gc
import ujson
import webrepl


webrepl.start()

try:
    os.stat('config.json')
except OSError:
    get_config()

with open('config.json', 'r') as file:
    config.CONFIG = ujson.load(file)

do_connect(config.CONFIG['ssid'], config.CONFIG['password'])

gc.collect()
