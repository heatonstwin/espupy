import os

import esp

import config
import time
from utilities import get_config

esp.osdebug(None)

import gc
import ujson
import webrepl


config.STARTUP_TIME = time.ticks_ms()
webrepl.start()

try:
    os.stat('config.json')
except OSError:
    get_config()

with open('config.json', 'r') as file:
    config.CONFIG = ujson.load(file)

gc.collect()
