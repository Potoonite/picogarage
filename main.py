## For controlling a garage door using a relay
## The relay is connected to the garage door opener
## The relay is connected to pin 0 of the PICO W

from machine import Pin
import time
import _thread
import json
import network
import secrets
from utime import sleep
import socket

# setup relay pin as output
relay = Pin(0, Pin.OUT)

# LED
led = machine.Pin("LED", machine.Pin.OUT)

lock = 0
state = 0

# Function to turn on and off relay
def relay_on_off(state):
    if state != 0 and state != 1:
        print("Invalid state")
        return
    relay.value(state)
    print("Relay On" if state == 0 else "Relay Off")

# Toggle relay for 500ms
def toggle_relay():
    relay_on_off(1)
    led.value(1)
    time.sleep(0.4)
    relay_on_off(0)
    led.value(0)
    time.sleep(0.1)

# Call Toggle relay in a separate thread, and have a lock and state to keep the next call from happening
def call_toggle_relay():
    global lock
    global state
    if lock == 0:
        lock = 1
        toggle_relay()
        lock = 0
        state = 0
        print("Relay toggled")
        return True
    else:
        print("Relay is busy")
        return False

# Define the HTTP request handler class
'''class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Check if the request path is '/'
        if self.path == '/action':
            # Check if the request content type is JSON
            if self.headers.get('Content-Type') == 'application/json':
                # Read the request body
                content_length = int(self.headers.get('Content-Length'))
                if content_length > 0 and content_length < 2000:
                    body = self.rfile.read(content_length)
                 
                    try:
                        # Parse the JSON payload
                        payload = json.loads(body)

                        # Process the payload
                        process_payload(payload)

                        # Send a response with HTTP status code 200 (OK)
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        response = {'success': True, 
                                    'message': 'Success'}
                        self.wfile.write(json.dumps(response).encode())

                    except json.JSONDecodeError:
                        # Send a response with HTTP status code 400 (Bad Request)
                        self.send_response(400)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        response = {'success': False, 
                                    'message': 'Invalid JSON payload'}
                        self.wfile.write(json.dumps(response).encode())
                    except InvalidPayloadError as e:
                        # Send a response with HTTP status code 400 (Bad Request)
                        self.send_response(400)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        response = {'success': False, 
                                    'message': str(e)}
                        self.wfile.write(json.dumps(response).encode())
                    except Exception as e:
                        # Send a response with HTTP status code 500 (Internal Server Error)
                        self.send_response(500)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        response = {'success': False, 
                                    'message': str(e)}
                        self.wfile.write(json.dumps(response).encode())
                else:
                    # Send a response with HTTP status code 400 (Bad Request)
                    self.send_response(400)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    response = {'success': False, 
                                'message': 'Invalid JSON payload'}
                    self.wfile.write(json.dumps(response).encode())
            else:
                # Send a response with HTTP status code 415 (Unsupported Media Type)
                self.send_response(415)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {'success': False, 
                            'message': 'Unsupported Media Type'}
                self.wfile.write(json.dumps(response).encode())

        else:
            # Send a response with HTTP status code 404 (Not Found)
            self.send_response(404)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {'success': False, 
                        'message': 'Not Found'}
            self.wfile.write(json.dumps(response).encode())
'''
class InvalidPayloadError(Exception):
    """Exception raised for invalid payload."""
    def __init__(self, payload, message="Invalid payload"):
        self.payload = payload
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message} -> {self.payload}'

# Function to process the JSON payload
def process_payload(payload):
    # JSON should contains a key called action
    if 'action' in payload:
        action = payload['action']
        if action == 'toggle':
            return call_toggle_relay()
        else:
            print("Invalid action")
            raise InvalidPayloadError(payload, "Invalid action")

    else:
        print("Invalid JSON payload")
        raise InvalidPayloadError(payload, "Invalid JSON payload")


# Attempt to start WiFi first
def connect_to_wifi(wlan):  
    print('Connecting to WiFi Network Name:', secrets.SSID)
    wlan.active(True) # power up the WiFi chip
    print('Waiting for wifi chip to power up...')
    # check wlan status until it is ready
    sleep(2)
    print('WiFi chip is ready.')    
    wlan.connect(secrets.SSID, secrets.PASSWORD)
    print('Waiting for access point to log us in.')
    maxwait = 5
    while wlan.isconnected() == False:
        sleep(1)
        maxwait -= 1
        
    if wlan.isconnected():
        print('Success! We have connected to your access point!')
        print('Try to ping the device at', wlan.ifconfig()[0])
    else:
        print('Failure! We have not connected to your access point!  Check your secrets.py file for errors.')
    return wlan.isconnected()

# a function that keeps checking for WiFi status every second, and resets the WiFi if it is not connected
def check_wifi(wlan, sleepTime=5):
    #while True:
        if not wlan.isconnected():
            print('WiFi is not connected.  Resetting WiFi.')
            #wlan.disconnect()
            sleep(2)
            if connect_to_wifi(wlan):
                print('Reset Successful')
            else:
                print('Reset Failed')
        else:
            sleep(sleepTime)

def blink_led(t):
    led.toggle()
    sleep(t)
    led.toggle()
    sleep(t)


def listen():
    global stopListen
    tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    tcpServer.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcpServer.settimeout(5) # timeout for listening
    tcpServer.bind(('0.0.0.0', 80)) # IP and PORT
    tcpServer.listen(1)
    while not stopListen:
        try: 
            (conn, (ip, port)) = tcpServer.accept() 
        except OSError as e:
            if e.errno == 110:
                #print("Checking WiFi")
                pass
            else:
                print(f"OSError: {e}. Checking WiFi")
            check_wifi(wlan, 0)
        except Exception as e:
            print(f"Error: {e}.")
        else:
            # work with the connection, create a thread etc.
            print('Got connection from', (ip, port))
            #print('Content = %s' % request)
            try: 
                request = conn.recv(1024)
                request = request.decode()

                ## Intentionally add a space to avoid reacting to /favicon.ico request
                if request.find('/toggle ') != -1:
                    print("Toggling relay")
                    ret = call_toggle_relay()
                    if ret:
                        conn.sendall('HTTP/1.1 200 OK\nContent-Type: application/json\n\n{"status": "OK", "op": "toggle"}'.encode())
                    else:
                        conn.sendall('HTTP/1.1 200 OK\nContent-Type: application/json\n\n{"status": "BUSY", "op": "toggle"}'.encode())
                elif request.find('/status ') != -1:
                    conn.sendall('HTTP/1.1 200 OK\nContent-Type: application/json\n\n{"status": "OK", "op": "status"}'.encode())
                elif request.find('/stop ') != -1:
                    print("Stopping server")
                    conn.sendall('HTTP/1.1 200 OK\nContent-Type: application/json\n\n{"status": "OK", "op": "stop"}'.encode())
                    break
                elif request.find('/favicon.ico ') != -1:
                    conn.sendall('HTTP/1.1 404 Not Found\nContent-Type: application/json\n\n{"status": "ERROR", "msg": "Not Found"}'.encode())
                else:
                    print('Content = %s' % request)
                    conn.sendall('HTTP/1.1 404 Not Found\nContent-Type: application/json\n\n{"status": "ERROR"}'.encode())
            except OSError as e:
                if e.errno == 110:
                    print("Receiving Timed Out")
                    check_wifi(wlan, 0)
                else:
                    print(f"OSError: {e}.")                    
            except Exception as e:
                conn.sendall('HTTP/1.1 200 OK\nContent-Type: application/json\n\n{"status": "ERROR", "msg": "{e}"}'.encode())
                print('Content = %s' % request)
                print(f"Error in request: {e}")
            finally:
                conn.close()
    print("Stopped Listening")
    tcpServer.close()

# MAIN
wlan = network.WLAN(network.STA_IF)
connect_to_wifi(wlan)

stopListen = False

print("Starting server")
listen()

