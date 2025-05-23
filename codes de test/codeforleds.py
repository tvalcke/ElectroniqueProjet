import network
import socket
from machine import Pin
import time

led = Pin(17, Pin.OUT)  # GPIO15

ssid = 'Proximus-Home-205507'
password = 'd44sx6x4a7yecppm'  # 🔁 Replace this with your actual WiFi password

# Connect to WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

print("🔌 Connecting to WiFi...")
while not wlan.isconnected():
    time.sleep(1)

ip = wlan.ifconfig()[0]
print("✅ Connected. Pico W IP Address:", ip)

# Set up simple web server
addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(addr)
s.listen(1)

print("🌐 Listening on http://" + ip)

while True:
    conn, addr = s.accept()
    print("📥 Client connected from", addr)
    request = conn.recv(1024).decode()
    print("📨 Request:", request)

    if 'GET /on' in request:
        led.on()
        print("💡 LED turned ON")
    elif 'GET /off' in request:
        led.off()
        print("🔌 LED turned OFF")

    response = "HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\n\r\nOK"
    conn.send(response)
    conn.close()
