from machine import Pin
import time

# Define BCD pins (A-D -> GPIO 3,2,1,0)
bcd_pins = [
    Pin(22, Pin.OUT),  # A (MSB)
    Pin(21, Pin.OUT),  # B
    Pin(20, Pin.OUT),  # C
    Pin(19, Pin.OUT)   # D (LSB)
]

def display_digit(digit):
    if digit < 0 or digit > 9:
        print("Digit must be 0-9")
        return
    binary = [int(x) for x in f"{digit:04b}"]
    for pin, val in zip(bcd_pins, binary):
        pin.value(val)
    print(f"Displayed {digit} -> BCD {binary}")

# Example: Count 0–9 repeatedly
while True:
    for i in range(10):
        display_digit(i)
        time.sleep(2)
