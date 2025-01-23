import requests
import json
import time
from datetime import datetime
import logging

class PowerAutomateIntegration:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        self.required_fields = {'timestamp', 'reading', 'status'}

    def send_reading(self, reading_data, max_retries=3):
        """Send sensor reading to Power Automate flow"""
        if not self._validate_reading(reading_data):
            logging.error("Invalid reading data format")
            return False

        retry_count = 0
        while retry_count < max_retries:
            try:
                response = requests.post(
                    self.webhook_url,
                    data=json.dumps(reading_data),
                    headers={'Content-Type': 'application/json'}
                )
                if response.status_code == 202:
                    return True
                    
                logging.warning(f"Request failed with status {response.status_code}")
                retry_count += 1
                time.sleep(1)  # Wait before retry
                
            except Exception as e:
                logging.error(f"Error sending reading: {str(e)}")
                retry_count += 1
                time.sleep(1)
                
        return False

    def _validate_reading(self, reading_data):
        """Validate reading data format"""
        return all(field in reading_data for field in self.required_fields)

    def process_batch_readings(self, readings):
        """Process multiple readings"""
        results = []
        for reading in readings:
            result = self.send_reading(reading)
            results.append(result)
        return results

class PowerAutomateConnector:
    def __init__(self, sensor_endpoint, command_endpoint):
        self.sensor_endpoint = sensor_endpoint
        self.command_endpoint = command_endpoint
        self.session = requests.Session()  # For connection pooling
        self.headers = {'Content-Type': 'application/json'}

    def send_sensor_data(self, level):
        """Handle sensor data transmission"""
        payload = json.dumps({'liquid_level': level})
        
        try:
            response = self.session.post(
                self.sensor_endpoint,
                headers=self.headers,
                data=payload,
                timeout=3
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"Sensor data POST failed: {str(e)}")
            return False

    def send_command(self, command):
        """Handle command transmission"""
        payload = json.dumps({'voice_command': command})
        
        try:
            response = self.session.post(
                self.command_endpoint,
                headers=self.headers,
                data=payload,
                timeout=3
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"Command POST failed: {str(e)}")
            return False

    async def send_potion_data(self, potion_data):
        """Handle potion data transmission"""
        payload = json.dumps({
            'potion_data': {
                'start_time': potion_data['start_time'],
                'ingredients': potion_data['ingredients'],
                'total_volume': potion_data['total_volume'],
                'completion_time': datetime.now().isoformat()
            }
        })
        
        try:
            response = await self.session.post(
                self.command_endpoint,
                headers=self.headers,
                data=payload,
                timeout=3
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logging.error(f"Potion data POST failed: {str(e)}")
            return False