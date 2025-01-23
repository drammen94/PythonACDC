import logging
import time
import asyncio
from sensor_script import LiquidLevelSensor
from voice_script import VoiceCommandRecognizer
from powerautomate_script import PowerAutomateConnector
from fastapi import FastAPI
from websocket_server import manager
from datetime import datetime
import os

class SystemIntegrator:
    def __init__(self, sensor, voice_recognizer, power_automate, websocket_url=None):
        self.sensor = sensor
        self.voice_recognizer = voice_recognizer
        self.power_automate = power_automate
        self.websocket_url = websocket_url
        # Make potion_mixer optional
        self.potion_mixer = None
        try:
            from potion_mixer import PotionMixer
            self.potion_mixer = PotionMixer(sensor, voice_recognizer, power_automate)
        except ImportError:
            logging.warning("PotionMixer module not available - some features will be disabled")
        
    async def process_sensor_reading(self):
        """Process and send sensor reading"""
        try:
            reading = self.sensor.get_filtered_reading()
            if reading is not None:
                # Send to Power Automate
                self.power_automate.send_sensor_data(reading)
                # Broadcast via WebSocket
                await manager.broadcast({
                    'type': 'sensor_reading',
                    'value': reading,
                    'timestamp': datetime.now().isoformat()
                })
                return True
            return False
        except Exception as e:
            logging.error(f"Error processing sensor reading: {str(e)}")
            return False

    async def process_voice_command(self):
        """Process voice commands for potion brewing"""
        try:
            command = self.voice_recognizer.listen_for_command()
            if not command:
                return False
                
            if 'start_potion' in command:
                return await self.potion_mixer.start_new_potion()
                
            if 'add_ingredient' in command:
                # Look for ingredient type in command
                ingredient_type = None
                for ing_type, keywords in self.voice_recognizer.command_keywords['ingredient_type'].items():
                    if any(keyword in command for keyword in keywords):
                        ingredient_type = ing_type
                        break
                        
                if ingredient_type:
                    return await self.potion_mixer.add_ingredient(ingredient_type)
                    
            if 'complete_potion' in command:
                return await self.potion_mixer.complete_potion()
                
            return False
            
        except Exception as e:
            logging.error(f"Error processing voice command: {str(e)}")
            return False

    async def run_monitoring_cycle(self, interval=5):
        """Run a full monitoring cycle"""
        results = {
            'sensor_success': False,
            'voice_success': False
        }
        
        try:
            results['sensor_success'] = await self.process_sensor_reading()
            await asyncio.sleep(interval)  # Wait between readings
            results['voice_success'] = await self.process_voice_command()
        except Exception as e:
            logging.error(f"Error in monitoring cycle: {str(e)}")
            
        return results

    async def cleanup(self):
        """Cleanup resources"""
        # Implementation of cleanup method
        pass

if __name__ == "__main__":
    # Initialize components
    sensor = LiquidLevelSensor()
    
    # Get API key from environment variable
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
        
    # Get Power Automate endpoints from environment variables
    sensor_endpoint = os.getenv('POWER_AUTOMATE_SENSOR_ENDPOINT')
    command_endpoint = os.getenv('POWER_AUTOMATE_COMMAND_ENDPOINT')
    
    if not sensor_endpoint or not command_endpoint:
        raise ValueError("Power Automate endpoints not configured in environment variables")
    
    voice_recognizer = VoiceCommandRecognizer(api_key=api_key)
    power_automate = PowerAutomateConnector(
        sensor_endpoint=sensor_endpoint,
        command_endpoint=command_endpoint
    )
    
    # WebSocket server will be running locally on the Raspberry Pi
    websocket_url = "ws://localhost:8000/ws"
    
    # Create and run integrator
    integrator = SystemIntegrator(
        sensor, 
        voice_recognizer, 
        power_automate,
        websocket_url
    )
    
    async def main():
        try:
            while True:
                results = await integrator.run_monitoring_cycle()
                logging.info(f"Monitoring cycle results: {results}")
        except KeyboardInterrupt:
            await integrator.cleanup()
    
    # Run the async main loop
    asyncio.run(main())