from machine import Pin
import time

# Change these pins if you’re using different ones
buttons = {
    "A": Pin(8, Pin.IN, Pin.PULL_UP),
    "B": Pin(9, Pin.IN, Pin.PULL_UP),
    "C": Pin(10, Pin.IN, Pin.PULL_UP),
    "D": Pin(11, Pin.IN, Pin.PULL_UP),
}

# Store previous states to detect new presses
last_states = {key: pin.value() for key, pin in buttons.items()}

print("🔧 Button test started. Press any button...")

while True:
    for label, pin in buttons.items():
        current = pin.value()
        if last_states[label] == 1 and current == 0:
            print(f"✅ Button {label} pressed")
        last_states[label] = current
    time.sleep(0.05)
