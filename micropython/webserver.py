import time
import ujson
import socket
import network


# HTML to send to browsers
html = """<!DOCTYPE html>
<html>
<head> <title>ESP8266 Config</title> </head>
<form>
<h1>{heading}</h1>
SSID (required): <input type="text" name="ssid"><br>
Password (required): <input type="text" name="password"><br>
Portal Server (required): <input type="text" name="server"><br>
Portal Port (optional): <input type="text" name="port"><br>
Portal Username (required): <input type="text" name="server_user"><br>
Portal Password (required): <input type="text" name="server_pass"><br>
Location (required): <input type="text" name="location"><br>
Sensor Type (required):
 <select name="sensor_type">
  <option value="dht11">DHT11</option>
 </select><br>
<input type="submit" value="Submit">
</form>
</html>
"""

REQUIRED_FIELDS = [
    'ssid',
    'password',
    'server',
    'server_user',
    'server_pass',
    'location',
    'sensor_type'
]


def serve():
    ap_if = network.WLAN(network.AP_IF)
    addr = socket.getaddrinfo(ap_if.ifconfig()[0], 80)[0][-1]
    sock = socket.socket()
    sock.bind(addr)
    sock.listen(5)
    print('listening on', addr)
    _exit = False
    while True:
        response = html.format(heading='Edit Configuration')
        conn, addr = sock.accept()
        print("Got a connection from %s" % str(addr))
        request = conn.recv(1024)
        print("Content = %s" % str(request.decode()))
        request = request.decode()
        content = [line for line in request.split('\r\n') if line.startswith('GET')]

        if content:
            content = content[0]

        if '/?' in content:
            # The first two characters will be /?
            raw_data = content.split()[1][2:]
            params = [item for item in raw_data.split('&')]
            data = dict([item.split('=') for item in params])

            if not all(data[field] for field in REQUIRED_FIELDS):
                response = html.format(heading='You must enter all required fields')
            else:
                _exit = True
                with open('config.json', 'w') as f:
                    f.write(ujson.dumps(data))
                response = ('<!DOCTYPE html>'
                            '<html>'
                            '<h1>Success!</h1>'
                            '<h2>Rebooting and attempting to join {ssid}</h2>'
                            '</html>').format(ssid=data['ssid'])
        conn.send(response)
        conn.close()
        if _exit is True:
            time.sleep_ms(2000)
            sock.close()
            break
