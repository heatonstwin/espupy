import time

import dht
import machine
import network
import sodrequests
import ujson

from utilities import pretty_mac
import config

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
    wlan = network.WLAN(network.STA_IF)
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
            # We need to touch this property so the request is processed
            # and the socket is closed
            _ = response.content

        time.sleep(int(sensor_data['sensor']['poll_rate']))


dht11 = dht.DHT11(machine.Pin(14))

while True:
    try:
        headers, csrf, sensor_data = setup()
    except OSError:
        pass
    else:
        break

run(headers, csrf, sensor_data, dht11)

