from machine import Pin
import time

# Rows as outputs (active LOW)
rows = [Pin(pin, Pin.OUT) for pin in [7,6,5,4]]

# Columns as inputs with pull-up resistors
cols = [Pin(pin, Pin.IN, Pin.PULL_UP) for pin in [3,2,1,0]]

# Adjusted keymap for your layout
key_map = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]

def scan_keypad():
    for row_index, row in enumerate(rows):
        row.value(0)  # Pull row LOW (active)
        for col_index, col in enumerate(cols):
            if col.value() == 0:  # Pressed key pulls column LOW
                row.value(1)  # Reset row HIGH
                return key_map[row_index][col_index]
        row.value(1)  # Set row HIGH again (inactive)
    return None

# Main loop
while True:
    key = scan_keypad()
    if key:
        print(f"Key Pressed: {key}")
        time.sleep(0.3)  # debounce
