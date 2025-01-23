import unittest
import asyncio
from unittest.mock import patch, MagicMock
from integration_script import SystemIntegrator
from sensor_script import LiquidLevelSensor
from voice_script import VoiceCommandRecognizer
from powerautomate_script import PowerAutomateConnector
import pytest

class TestSystemIntegration(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        # Mock dependencies
        self.mock_sensor = MagicMock(spec=LiquidLevelSensor)
        self.mock_voice = MagicMock(spec=VoiceCommandRecognizer)
        self.mock_connector = MagicMock(spec=PowerAutomateConnector)
        
        # Create integrator with mock components
        self.integrator = SystemIntegrator(
            sensor=self.mock_sensor,
            voice_recognizer=self.mock_voice,
            power_automate=self.mock_connector
        )
        
        # Sample test data
        self.test_level = 25.5
        self.test_command = ["start", "production"]

    @pytest.mark.asyncio
    async def test_process_sensor_reading(self):
        """Test sensor reading processing"""
        # Setup mock returns
        self.mock_sensor.get_filtered_reading.return_value = self.test_level
        self.mock_connector.send_sensor_data.return_value = True

        # Test successful processing
        result = await self.integrator.process_sensor_reading()
        assert result is True
        
        # Verify interactions
        self.mock_sensor.get_filtered_reading.assert_called_once()
        self.mock_connector.send_sensor_data.assert_called_once_with(self.test_level)

    async def test_process_sensor_reading_failure(self):
        """Test handling of sensor reading failures"""
        # Setup mock for failure
        self.mock_sensor.get_filtered_reading.return_value = None

        # Test failed processing
        result = await self.integrator.process_sensor_reading()
        self.assertFalse(result)
        self.mock_connector.send_sensor_data.assert_not_called()

    async def test_process_voice_command(self):
        """Test voice command processing"""
        # Setup mock returns
        self.mock_voice.listen_for_command.return_value = self.test_command
        self.mock_connector.send_command.return_value = True

        # Test successful processing
        result = await self.integrator.process_voice_command()
        self.assertTrue(result)
        
        # Verify interactions
        self.mock_voice.listen_for_command.assert_called_once()
        self.mock_connector.send_command.assert_called_once_with(self.test_command)

    async def test_process_voice_command_failure(self):
        """Test handling of voice command failures"""
        # Setup mock for failure
        self.mock_voice.listen_for_command.return_value = None

        # Test failed processing
        result = await self.integrator.process_voice_command()
        self.assertFalse(result)
        self.mock_connector.send_command.assert_not_called()

    async def test_run_monitoring_cycle(self):
        """Test full monitoring cycle"""
        # Setup mocks
        self.mock_sensor.get_filtered_reading.return_value = self.test_level
        self.mock_voice.listen_for_command.return_value = self.test_command
        self.mock_connector.send_sensor_data.return_value = True
        self.mock_connector.send_command.return_value = True

        # Test cycle execution
        with patch('asyncio.sleep', return_value=None):  # Prevent actual sleeping
            results = await self.integrator.run_monitoring_cycle()
            
        # Verify results
        self.assertTrue(results['sensor_success'])
        self.assertTrue(results['voice_success'])

    async def test_error_handling(self):
        """Test error handling in monitoring cycle"""
        # Setup mocks to raise exceptions
        self.mock_sensor.get_filtered_reading.side_effect = Exception("Sensor error")
        self.mock_voice.listen_for_command.side_effect = Exception("Voice error")

        # Test error handling
        with patch('asyncio.sleep', return_value=None):
            results = await self.integrator.run_monitoring_cycle()
            
        # Verify error handling
        self.assertFalse(results['sensor_success'])
        self.assertFalse(results['voice_success'])

    @patch('logging.error')
    async def test_logging(self, mock_logging):
        """Test logging functionality"""
        # Trigger error condition
        self.mock_sensor.get_filtered_reading.side_effect = Exception("Test error")
        await self.integrator.process_sensor_reading()
        
        # Verify error was logged
        mock_logging.assert_called()
        self.assertIn("Test error", str(mock_logging.call_args))

if __name__ == '__main__':
    unittest.main() 