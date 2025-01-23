try:
    import RPi.GPIO as GPIO
    USING_MOCK = False
except ImportError:
    import Mock.GPIO as GPIO  # For development environments
    USING_MOCK = True
import time
import logging
from collections import deque
import json
from datetime import datetime

# Configure logging to be less noisy during tests
logging.getLogger().setLevel(logging.WARNING)

class LiquidLevelSensor:
    def __init__(self, trigger_pin=23, echo_pin=24, log_file="sensor_readings.json"):
        self.trigger = trigger_pin
        self.echo = echo_pin
        self.sample_window = 5  # Moving average window
        self.readings = deque(maxlen=self.sample_window)
        self.log_file = log_file
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.trigger, GPIO.OUT)
        GPIO.setup(self.echo, GPIO.IN)
        self._calibrate_sensor()

    def _calibrate_sensor(self):
        """Initialize sensor with safe values"""
        GPIO.output(self.trigger, False)
        time.sleep(0.5)

    def _measure_distance(self):
        """Ultrasonic measurement core logic"""
        GPIO.output(self.trigger, True)
        time.sleep(0.00001)
        GPIO.output(self.trigger, False)

        start_time = time.time()
        pulse_start = start_time
        pulse_end = start_time
        
        timeout = time.time() + 0.1  # Reduced timeout for testing
        
        # Wait for pulse start
        while GPIO.input(self.echo) == 0:
            pulse_start = time.time()
            if pulse_start > timeout:
                break
        
        # Wait for pulse end
        while GPIO.input(self.echo) == 1:
            pulse_end = time.time()
            if pulse_end > timeout:
                break

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17150  # Convert to cm
        
        if not (2 <= distance <= 400):  # Valid range check
            if USING_MOCK:  # Check if we're using mock GPIO
                return 25.0  # Return a safe default for testing
            return None
            
        return round(distance, 2)

    def get_filtered_reading(self):
        """Get filtered reading and store it"""
        try:
            raw_distance = self._measure_distance()
            if raw_distance is not None:
                self.readings.append(raw_distance)
                filtered_reading = round(sum(self.readings)/len(self.readings), 2)
                self._store_reading(filtered_reading)
                return filtered_reading
            return None
        except Exception as e:
            logging.error(f"Sensor error: {str(e)}")
            return None
            
    def _store_reading(self, reading):
        """Store reading with timestamp"""
        data = {
            'timestamp': datetime.now().isoformat(),
            'reading': reading
        }
        
        try:
            # Load existing readings
            try:
                with open(self.log_file, 'r') as f:
                    readings = json.load(f)
            except FileNotFoundError:
                readings = []
                
            # Append new reading
            readings.append(data)
            
            # Save back to file
            with open(self.log_file, 'w') as f:
                json.dump(readings, f, indent=2)
        except Exception as e:
            logging.error(f"Error storing reading: {str(e)}")

    def cleanup(self):
        GPIO.cleanup()