import pytest
import asyncio
from unittest.mock import patch, MagicMock
from integration_script import SystemIntegrator
from sensor_script import LiquidLevelSensor
from voice_script import VoiceCommandRecognizer
from powerautomate_script import PowerAutomateConnector

@pytest.mark.asyncio
class TestSystemIntegration:
    @pytest.fixture(autouse=True)
    async def setup(self):
        """Set up test environment"""
        # Mock dependencies
        self.mock_sensor = MagicMock(spec=LiquidLevelSensor)
        self.mock_voice = MagicMock(spec=VoiceCommandRecognizer)
        self.mock_connector = MagicMock(spec=PowerAutomateConnector)
        
        # Create mock potion mixer with async methods
        class AsyncMock(MagicMock):
            async def __call__(self, *args, **kwargs):
                return super(AsyncMock, self).__call__(*args, **kwargs)
        
        self.mock_potion_mixer = AsyncMock()
        self.mock_potion_mixer.start_new_potion = AsyncMock(return_value=True)
        self.mock_potion_mixer.add_ingredient = AsyncMock(return_value=True)
        self.mock_potion_mixer.complete_potion = AsyncMock(return_value=True)
        
        # Create integrator with mock components
        self.integrator = SystemIntegrator(
            sensor=self.mock_sensor,
            voice_recognizer=self.mock_voice,
            power_automate=self.mock_connector
        )
        
        # Add mock potion mixer
        self.integrator.potion_mixer = self.mock_potion_mixer
        
        # Sample test data
        self.test_level = 25.5
        self.test_command = ["start_potion"]
        
        # Setup command keywords
        self.mock_voice.command_keywords = {
            'ingredient_type': {
                'herb': ['herb', 'herbs'],
                'crystal': ['crystal', 'crystals']
            }
        }
        
        yield
        
        # Cleanup after tests
        await self.integrator.cleanup()

    async def test_process_sensor_reading(self):
        """Test sensor reading processing"""
        self.mock_sensor.get_filtered_reading.return_value = self.test_level
        self.mock_connector.send_sensor_data.return_value = True

        result = await self.integrator.process_sensor_reading()
        assert result is True
        self.mock_connector.send_sensor_data.assert_called_once_with(self.test_level)

    async def test_process_sensor_reading_failure(self):
        """Test handling of sensor reading failures"""
        self.mock_sensor.get_filtered_reading.return_value = None
        result = await self.integrator.process_sensor_reading()
        assert result is False
        self.mock_connector.send_sensor_data.assert_not_called()

    async def test_process_voice_command(self):
        """Test voice command processing"""
        self.mock_voice.listen_for_command.return_value = self.test_command
        self.mock_potion_mixer.start_new_potion.return_value = True

        result = await self.integrator.process_voice_command()
        assert result is True
        self.mock_voice.listen_for_command.assert_called_once()
        self.mock_potion_mixer.start_new_potion.assert_called_once()

    async def test_process_voice_command_failure(self):
        """Test handling of voice command failures"""
        self.mock_voice.listen_for_command.return_value = None
        result = await self.integrator.process_voice_command()
        assert result is False
        self.mock_potion_mixer.start_new_potion.assert_not_called()

    async def test_run_monitoring_cycle(self):
        """Test full monitoring cycle"""
        self.mock_sensor.get_filtered_reading.return_value = self.test_level
        self.mock_voice.listen_for_command.return_value = self.test_command
        self.mock_connector.send_sensor_data.return_value = True
        self.mock_potion_mixer.start_new_potion.return_value = True

        with patch('asyncio.sleep', return_value=None):
            results = await self.integrator.run_monitoring_cycle()
        
        assert results['sensor_success'] is True
        assert results['voice_success'] is True

    async def test_error_handling(self):
        """Test error handling in monitoring cycle"""
        self.mock_sensor.get_filtered_reading.side_effect = Exception("Sensor error")
        self.mock_voice.listen_for_command.side_effect = Exception("Voice error")

        with patch('asyncio.sleep', return_value=None):
            results = await self.integrator.run_monitoring_cycle()
        
        assert results['sensor_success'] is False
        assert results['voice_success'] is False

    async def test_logging(self):
        """Test logging functionality"""
        with patch('logging.error') as mock_logging:
            self.mock_sensor.get_filtered_reading.side_effect = Exception("Test error")
            await self.integrator.process_sensor_reading()
            
            mock_logging.assert_called()
            assert "Test error" in str(mock_logging.call_args)

if __name__ == '__main__':
    pytest.main([__file__, '-v']) 