import time

import dht
import machine
import network
import sodrequests
import ujson

from utilities import pretty_mac
import config

from utilities import do_connect

do_connect(config.CONFIG['ssid'], config.CONFIG['password'])
wlan = network.WLAN(network.STA_IF)
dht11 = dht.DHT11(machine.Pin(14))
rtc = machine.RTC()
rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)

HOST = config.CONFIG['server']
port = config.CONFIG['port']

if port:
    HOST += ':{}'.format(port)

URL = 'http://{}'.format(HOST)


def fahrenheit(temp):
    return (temp * 1.8) + 32


def setup():
    headers = {'Referer': '{}/admin/login/'.format(HOST)}

    response = sodrequests.get('{}/admin/login/'.format(URL), headers=headers)
    cookie = [line.split()[1].strip(';') for line in response.headers.split('\n') if line.startswith('Set-Cookie')][0]

    headers['Content-Type'] = 'application/x-www-form-urlencoded'
    headers['Cookie'] = cookie

    csrf = {'csrfmiddlewaretoken': cookie.split('=')[1]}
    login = {'username': config.CONFIG['server_user'], 'password': config.CONFIG['server_pass']}
    login.update(csrf)
    response = sodrequests.post('{}/admin/login/'.format(URL), data=login, headers=headers)

    if response.status_code != 302:
        return

    payload = {
        'mac': pretty_mac(),
        'device': 'DHT11'
    }

    payload.update(csrf)
    payload.update(dict(zip(['address', 'netmask', 'gateway', 'dns'], wlan.ifconfig())))
    del payload['dns']
    response = sodrequests.post('{}/sensor/register'.format(URL), data=payload, headers=headers)

    sensor_data = ujson.loads(response.text)
    return headers, csrf, sensor_data


def run(headers, csrf, sensor_data, sensor):
    while True:
        update_sensor_data_response = sodrequests.get('{}/sensor/{}'.format(URL,
                                                                            sensor_data['sensor']['id']))
        sensor_data = ujson.loads(update_sensor_data_response.text)
        sensor.measure()
        temp = fahrenheit(sensor.temperature())

        payload = {
            'sensor': str(sensor_data['sensor']['id']),
            'unit': 'F',
            'measurement': '%.2f' % temp
        }

        payload.update(csrf)
        try:
            response = sodrequests.post('{}/sensor/sense'.format(URL), data=payload, headers=headers)
        except OSError:
            pass
        else:
            print('post_request={}'.format(time.ticks_ms()))
            # We need to touch this property so the request is processed
            # and the socket is closed
            data = ujson.loads(response.content.decode())

            # Get the amount of time we should sleep from the response and cut 30 seconds
            # off of it so we have time to wake up and get setup done
            sleep_time_ms = (int(data['sleep']) - config.WAKE_AHEAD_SEC) * 1000
            print('data={}'.format(data))
            print('sleep={}'.format(int(data['sleep'])))
            print('deep_sleep={}'.format(sleep_time_ms))
            rtc.alarm(rtc.ALARM0, sleep_time_ms)
            machine.deepsleep()


setup_start = time.ticks_ms()
while True:
    try:
        headers, csrf, sensor_data = setup()
    except OSError:
        pass
    else:
        break
setup_end = time.ticks_ms()
print('setup_start={}'.format(setup_start))
print('setup_end={}'.format(setup_end))

# To keep on a regular update schedule we want to figure out
# how long it took us to boot up and connect to the database.
# Since we are booting up config.WAKE_AHEAD_SEC of the next report
# interval we need to calculate any additional sleep time.
now = time.ticks_ms()
boot_time = now - config.STARTUP_TIME
print('startup_time={}'.format(config.STARTUP_TIME))
print('now={}'.format(now))
print('boot_time={}'.format(boot_time))
delay = (config.WAKE_AHEAD_SEC * 1000) - boot_time

if delay > 0:
    print('delay={}'.format(delay - 200))
    # Shave off about 750 ms from the sleep time so we don't over shoot
    # the update time
    time.sleep_ms(delay - 750)

print('pre-run={}'.format(time.ticks_ms()))
run(headers, csrf, sensor_data, dht11)

