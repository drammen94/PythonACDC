import unittest
from sensor_script import LiquidLevelSensor
import time
import json
import os

class TestLiquidLevelSensor(unittest.TestCase):
    def setUp(self):
        self.test_log_file = "test_readings.json"
        self.sensor = LiquidLevelSensor(trigger_pin=23, echo_pin=24, log_file=self.test_log_file)
    
    def tearDown(self):
        self.sensor.cleanup()
        # Clean up test file
        if os.path.exists(self.test_log_file):
            os.remove(self.test_log_file)
    
    def test_sensor_initialization(self):
        """Test if sensor initializes properly"""
        self.assertEqual(self.sensor.trigger, 23)
        self.assertEqual(self.sensor.echo, 24)
        self.assertEqual(self.sensor.sample_window, 5)
    
    def test_filtered_reading(self):
        """Test if sensor returns filtered reading"""
        # Take multiple readings to fill the deque
        readings = []
        for _ in range(5):
            reading = self.sensor.get_filtered_reading()
            if reading is not None:
                readings.append(reading)
            time.sleep(0.1)
        
        self.assertTrue(len(readings) > 0, "Should get at least one valid reading")
        self.assertTrue(all(isinstance(r, float) for r in readings))
        self.assertTrue(all(2 < r < 400 for r in readings))
    
    def test_reading_storage(self):
        """Test if readings are properly stored"""
        # Get multiple readings
        valid_readings = 0
        max_attempts = 10
        attempts = 0
        
        while valid_readings < 3 and attempts < max_attempts:
            reading = self.sensor.get_filtered_reading()
            if reading is not None:
                valid_readings += 1
            attempts += 1
            time.sleep(0.1)
        
        # Verify file exists and contains readings
        self.assertTrue(os.path.exists(self.test_log_file))
        with open(self.test_log_file, 'r') as f:
            readings = json.load(f)
            self.assertGreater(len(readings), 0)
            self.assertTrue(all('timestamp' in r and 'reading' in r for r in readings))

if __name__ == '__main__':
    unittest.main()