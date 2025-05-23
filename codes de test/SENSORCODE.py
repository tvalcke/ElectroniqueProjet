from machine import Pin, time_pulse_us
import time

# Define pins
TRIG_PIN = 17
ECHO_PIN = 18

trig = Pin(TRIG_PIN, Pin.OUT)
echo = Pin(ECHO_PIN, Pin.IN)

def get_distance():
    # Ensure trigger is low
    trig.value(0)
    time.sleep_us(2)

    # Send a 10us pulse to trigger
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)

    # Measure the duration of the echo pulse
    duration = time_pulse_us(echo, 1, 30000)  # 30 ms timeout

    # If timeout occurred
    if duration < 0:
        return None

    # Calculate distance (speed of sound ~343 m/s)
    distance_cm = (duration * 0.0343) / 2  # Or: duration / 58.0
    return distance_cm

# Main loop
while True:
    distance = get_distance()
    if distance is None:
        print("Out of range")
    else:
        print("Distance: {:.2f} cm".format(distance))
    time.sleep(1)
