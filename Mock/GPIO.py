# Mock GPIO for development environments
import time
import random

BCM = "BCM"
IN = "IN"
OUT = "OUT"

class MockState:
    def __init__(self):
        self.echo_start = 0
        self.is_echo_active = False
        self.distance = random.uniform(20, 30)  # Random distance between 20-30cm

_state = MockState()

def setmode(mode):
    pass

def setup(pin, mode):
    pass

def output(pin, value):
    if value:  # Trigger pulse started
        _state.echo_start = time.time()
        _state.is_echo_active = True
        # Generate new random distance for next reading
        _state.distance = random.uniform(20, 30)

def input(pin):
    if not _state.is_echo_active:
        return 0
    
    # Calculate time delay based on distance
    # Speed of sound = 343 m/s = 34300 cm/s
    # Time = distance * 2 / speed (multiply by 2 for round trip)
    delay = (_state.distance * 2) / 34300
    
    elapsed = time.time() - _state.echo_start
    if elapsed < 0.00001:  # Initial delay
        return 0
    elif elapsed < delay:  # Echo pulse
        return 1
    else:
        _state.is_echo_active = False
        return 0

def cleanup():
    pass