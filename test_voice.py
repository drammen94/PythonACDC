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
import unittest
from unittest.mock import patch, MagicMock

# Load environment variables from .env file
load_dotenv()

# Configure OpenAI with API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

class VoiceCommandRecognizer:
    def __init__(self, api_key, model="whisper-1"):
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.command_keywords = {
            'start': ['begin', 'start', 'initiate'],
            'production': ['production', 'process', 'manufacturing'],
            'consume': ['consume', 'use', 'utilize'],
            'finish': ['complete', 'finish', 'finalize']
        }
        self.sample_rate = 16000  # Whisper recommended sample rate
        self.channels = 1
        self.silence_threshold = 0.03  # Adjust based on microphone sensitivity

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

class TestVoiceCommandRecognizer(unittest.TestCase):
    def setUp(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.recognizer = VoiceCommandRecognizer(api_key=self.api_key)

    def test_initialization(self):
        """Test if VoiceCommandRecognizer initializes properly"""
        self.assertEqual(self.recognizer.model, "whisper-1")
        self.assertEqual(self.recognizer.sample_rate, 16000)
        self.assertEqual(self.recognizer.channels, 1)

    @patch('sounddevice.InputStream')
    def test_record_audio(self, mock_input_stream):
        """Test audio recording functionality"""
        # Mock audio data
        mock_audio = np.random.rand(16000 * 5)  # 5 seconds of random audio
        
        # Setup mock input stream
        mock_context = MagicMock()
        mock_input_stream.return_value = mock_context
        
        # Test recording
        with patch.object(self.recognizer, '_record_audio', return_value=mock_audio):
            audio_data = self.recognizer._record_audio()
            self.assertIsNotNone(audio_data)
            self.assertEqual(len(audio_data), 16000 * 5)

    def test_parse_command(self):
        """Test command parsing functionality"""
        # Test valid commands
        text = "start production process"
        result = self.recognizer._parse_command(text)
        self.assertIn('start', result)
        self.assertIn('production', result)

        # Test invalid command
        text = "random text without commands"
        result = self.recognizer._parse_command(text)
        self.assertIsNone(result)

        # Test empty input
        result = self.recognizer._parse_command("")
        self.assertIsNone(result)

    @patch('openai.Audio')
    def test_transcribe_audio(self, mock_audio):
        """Test audio transcription"""
        # Mock audio data and OpenAI response
        mock_audio_data = np.random.rand(16000 * 2)  # 2 seconds of random audio
        mock_audio.transcribe.return_value = {"text": "start production"}
        
        with patch.object(self.recognizer, '_transcribe_audio') as mock_transcribe:
            mock_transcribe.return_value = "start production"
            transcription = self.recognizer._transcribe_audio(mock_audio_data)
            self.assertEqual(transcription, "start production")

    def test_command_keywords(self):
        """Test command keyword matching"""
        keywords = self.recognizer.command_keywords
        
        # Test each command category
        self.assertIn('begin', keywords['start'])
        self.assertIn('production', keywords['production'])
        self.assertIn('consume', keywords['consume'])
        self.assertIn('finish', keywords['finish'])

# Example usage
if __name__ == "__main__":
    unittest.main()
