import ujson
import socket
import machine


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
Location (required): <input type="text" name="location"><br>
Sensor Type (required):
 <select name="sensor_type">
  <option value="dht11">DHT11</option>
 </select><br>
<input type="submit" value="Submit">
</form>
</html>
"""

REQUIRED_FIELDS = ['ssid', 'password', 'server', 'location', 'sensor_type']


# Setup Socket WebServer
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('', 80))
sock.listen(5)


def serve():
    exit = False
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
                exit = True
                with open('config.json', 'w') as f:
                    f.write(ujson.dumps(data))
                response = ('<!DOCTYPE html>'
                            '<html>'
                            '<h1>Success!</h1>'
                            '<h2>Rebooting and attempting to join {ssid}</h2>'
                            '</html>').format(ssid=data['ssid'])
        conn.send(response)
        conn.close()
        if exit is True:
            return
