from machine import Pin
import time

# Create a list of LED pin objects for GPIO 12 to 16
led_pins = [12, 13, 14, 15, 16]
leds = [Pin(pin, Pin.OUT) for pin in led_pins]

while True:
    # Turn all LEDs on
    for led in leds:
        led.on()
    time.sleep(1)

    # Turn all LEDs off
    for led in leds:
        led.off()
    time.sleep(1)
