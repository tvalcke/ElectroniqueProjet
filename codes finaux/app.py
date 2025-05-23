from machine import Pin, time_pulse_us
import network
import time
import urequests
import ujson

# ——— Wi-Fi setup ———
ssid = 'Proximus-Home-205507'
password = 'd44sx6x4a7yecppm'
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)
while not wlan.isconnected():
    time.sleep(1)
print("Connected, IP =", wlan.ifconfig()[0])

# ——— Server URLs ———
FLASK_SERVER = 'http://192.168.129.15:5000'
# Ensure correct slash before 'sensor'
FIREBASE_URL = (
    'https://anime-time-bomb-default-rtdb.europe-west1.firebasedatabase.app'
    '/sensor/distances.json'
)

# ——— HC-SR04 sensor setup ———
TRIG_PIN = 17
ECHO_PIN = 18
trig = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)

def get_distance():
    trig.value(0)
    time.sleep_us(2)
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)
    duration = time_pulse_us(echo, 1, 30000)
    if duration < 0:
        return None
    return (duration * 0.0343) / 2

# ——— Firebase push helper ———
# Use ujson and explicit headers for reliability
def push_distance_to_firebase(distance_cm):
    payload = {'distance_cm': distance_cm, 'ts': int(time.time())}
    try:
        data = ujson.dumps(payload)
        headers = {'Content-Type': 'application/json'}
        resp = urequests.post(FIREBASE_URL, data=data, headers=headers)
        print('Firebase:', resp.status_code, resp.text)
        resp.close()
    except Exception as e:
        print('❌ Firebase ERROR:', e)

# ——— Buttons A-D setup ———
buttons = {
    'A': Pin(8, Pin.IN, Pin.PULL_UP),
    'B': Pin(9, Pin.IN, Pin.PULL_UP),
    'C': Pin(10, Pin.IN, Pin.PULL_UP),
    'D': Pin(11, Pin.IN, Pin.PULL_UP),
}
last_states = {k: v.value() for k, v in buttons.items()}

# ——— 7-segment display setup ———
bcd_pins = [Pin(22, Pin.OUT), Pin(21, Pin.OUT), Pin(20, Pin.OUT), Pin(19, Pin.OUT)]
disp1 = Pin(26, Pin.OUT)
disp2 = Pin(27, Pin.OUT)

def display_digit(d):
    bits = [(d >> i) & 1 for i in (3, 2, 1, 0)]
    for pin, b in zip(bcd_pins, bits):
        pin.value(b)

def update_display(score):
    score = min(max(score, 0), 99)
    display_digit(score // 10)
    disp1.value(1); time.sleep(0.003); disp1.value(0)
    display_digit(score % 10)
    disp2.value(1); time.sleep(0.003); disp2.value(0)

# ——— Heart LEDs (lives) ———
heart_pins = [13, 14, 15]
hearts = [Pin(p, Pin.OUT) for p in heart_pins]

def update_hearts(lives):
    for i, h in enumerate(hearts):
        h.value(1 if i < lives else 0)

# ——— Game state ———
score = 0
lives = 3
update_hearts(lives)

# ——— Send answer & push sensor on button press ———
def send_answer(ans):
    global score, lives
    try:
        # 1) Send quiz answer to Flask
        r = urequests.post(f"{FLASK_SERVER}/submit_answer", json={'answer': ans})
        data = r.json()
        r.close()
        print('Flask response:', data)

        # 2) Update score & lives
        score = max(score, data.get('score', score))
        if data.get('result') == 'incorrect':
            lives -= 1
            update_hearts(lives)
            if lives <= 0:
                print('💥 Game Over')
                try:
                    urequests.get(f"{FLASK_SERVER}/game_over")
                except:
                    pass

        # 3) Read sensor & push to Firebase
        dist = get_distance()
        if dist is not None:
            print(f'Pushing dist {dist:.2f} cm')
            push_distance_to_firebase(dist)
        else:
            print('Sensor out of range; skipping Firebase push')

    except Exception as e:
        print('Error in send_answer():', e)

# ——— Main loop ———
while True:
    for label, pin in buttons.items():
        cur = pin.value()
        if last_states[label] == 1 and cur == 0:
            if lives > 0:
                print('Button pressed:', label)
                send_answer(label)
            else:
                print('Game over – input ignored')
        last_states[label] = cur

    update_display(score)