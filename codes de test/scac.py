from machine import Pin
import time

# Define GPIO numbers (for physical pins 14–17)
led_pins = [10, 11, 12, 13]

# Create LED output pins
leds = [Pin(pin, Pin.OUT) for pin in led_pins]

# Turn all LEDs ON
for led in leds:
    led.value(1)

print("LEDs on!")

# Wait 5 seconds
time.sleep(5)

# Turn all LEDs OFF
for led in leds:
    led.value(0)

print("LEDs off!")
