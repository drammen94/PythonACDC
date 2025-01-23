# Pro-Code Potions: Advanced audio processing
# Thieving Bastards: OpenAI Whisper API integration

from openai import OpenAI
import logging
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import tempfile
import time
from dotenv import load_dotenv
import os
import openai
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Configure OpenAI with API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

class VoiceCommandRecognizer:
    def __init__(self, api_key, model="whisper-1"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.command_keywords = {
            'start_potion': ['begin potion', 'start potion', 'create potion'],
            'add_ingredient': ['added', 'inserted', 'mixed in'],
            'ingredient_type': {
                'dragon_blood': ['dragon blood', 'blood of dragon'],
                'phoenix_tears': ['phoenix tears', 'tears of phoenix'],
                'unicorn_hair': ['unicorn hair', 'hair of unicorn'],
                'mandrake_root': ['mandrake root', 'root of mandrake']
            },
            'complete_potion': ['complete elixir', 'finish potion', 'finalize mixture']
        }
        self.sample_rate = 16000
        self.channels = 1
        self.silence_threshold = 0.03

    def _record_audio(self, duration=5):
        """Capture audio from microphone with voice activity detection"""
        print("Listening...")
        audio_data = []
        
        def callback(indata, frames, time, status):
            if status:
                print(f"Error in audio stream: {status}")
            if np.max(np.abs(indata)) > self.silence_threshold:
                audio_data.extend(indata.copy())
        
        with sd.InputStream(samplerate=self.sample_rate,
                            channels=self.channels,
                            callback=callback):
            start_time = time.time()
            while len(audio_data) < self.sample_rate * duration:
                if time.time() - start_time > duration:
                    break
                sd.sleep(100)
        
        if len(audio_data) == 0:
            print("No audio detected.")
            return None
            
        return np.concatenate(audio_data).astype(np.float32)

    def _transcribe_audio(self, audio_data):
        """Use Whisper API to transcribe audio"""
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
            write(tmpfile.name, self.sample_rate, audio_data)
            
            try:
                with open(tmpfile.name, "rb") as audio_file:
                    response = self.client.audio.transcriptions.create(
                        model=self.model,
                        file=audio_file,
                        response_format="text"
                    )
                return response.strip()
            except Exception as e:
                logging.error(f"Whisper API error: {str(e)}")
                return None
            finally:
                tmpfile.close()

    def _parse_command(self, text):
        """Enhanced command parsing with confidence scoring"""
        if not text:
            return None
            
        text = text.lower()
        command_scores = {category: 0 for category in self.command_keywords}
        
        for category, keywords in self.command_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    command_scores[category] += 1
        
        # Threshold for valid command detection
        if max(command_scores.values()) >= 1:
            return [k for k, v in command_scores.items() if v > 0]
        return None

    def listen_for_command(self, timeout=5):
        """Full voice command processing pipeline"""
        try:
            audio_data = self._record_audio(duration=timeout)
            if audio_data is None:
                return None
                
            transcription = self._transcribe_audio(audio_data)
            if transcription:
                print(f"Transcribed: {transcription}")
            return self._parse_command(transcription)
        except Exception as e:
            logging.error(f"Voice processing failed: {str(e)}")
            return None

class PotionMixer:
    def __init__(self, sensor, voice_recognizer, power_automate):
        self.sensor = sensor
        self.voice_recognizer = voice_recognizer
        self.power_automate = power_automate
        self.current_potion = None
        self.last_measurement = None
        self.ingredients = []
        
    async def start_new_potion(self):
        """Initialize a new potion brewing session"""
        self.current_potion = {
            'start_time': datetime.now().isoformat(),
            'ingredients': [],
            'total_volume': 0
        }
        self.last_measurement = await self.sensor.get_filtered_reading()
        return True
        
    async def add_ingredient(self, ingredient_type):
        """Record addition of new ingredient"""
        if not self.current_potion:
            return False
            
        current_measurement = await self.sensor.get_filtered_reading()
        if current_measurement is None:
            return False
            
        # Calculate volume added
        volume_added = current_measurement - self.last_measurement
        
        ingredient = {
            'type': ingredient_type,
            'volume': volume_added,
            'timestamp': datetime.now().isoformat()
        }
        
        self.current_potion['ingredients'].append(ingredient)
        self.current_potion['total_volume'] += volume_added
        self.last_measurement = current_measurement
        
        return True
        
    async def complete_potion(self):
        """Finalize the potion brewing process"""
        if not self.current_potion:
            return False
            
        # Send final potion data to Power Automate
        result = await self.power_automate.send_potion_data(self.current_potion)
        
        if result:
            self.current_potion = None
            self.last_measurement = None
            return True
        return False

# Example usage
if __name__ == "__main__":
    recognizer = VoiceCommandRecognizer(api_key=openai.api_key)
    while True:
        command = recognizer.listen_for_command()
        if command:
            print(f"Detected command(s): {command}")
        else:
            print("No command detected or could not understand.")
        
        user_input = input("Press Enter to listen again, or type 'q' to quit: ")
        if user_input.lower() == 'q':
            break
