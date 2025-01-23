import unittest
from unittest.mock import patch, MagicMock
import json
import os
from datetime import datetime
from powerautomate_script import PowerAutomateIntegration

class TestPowerAutomateIntegration(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.test_url = "https://test-flow.maker.powerautomate.com/trigger"
        self.power_automate = PowerAutomateIntegration(webhook_url=self.test_url)
        
        # Sample test data
        self.test_reading = {
            'timestamp': datetime.now().isoformat(),
            'reading': 25.5,
            'status': 'normal'
        }

    @patch('requests.post')
    def test_send_reading(self, mock_post):
        """Test sending sensor reading to Power Automate"""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 202
        mock_post.return_value = mock_response

        # Test successful send
        result = self.power_automate.send_reading(self.test_reading)
        self.assertTrue(result)
        mock_post.assert_called_once()
        
        # Verify JSON payload
        call_args = mock_post.call_args
        sent_data = json.loads(call_args[1]['data'])
        self.assertEqual(sent_data['reading'], 25.5)
        self.assertEqual(sent_data['status'], 'normal')

    @patch('requests.post')
    def test_send_reading_failure(self, mock_post):
        """Test handling of failed API calls"""
        # Setup mock response for failure
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        # Test failed send
        result = self.power_automate.send_reading(self.test_reading)
        self.assertFalse(result)

    def test_validate_reading(self):
        """Test reading validation"""
        # Test valid reading
        valid_reading = self.test_reading.copy()
        self.assertTrue(self.power_automate._validate_reading(valid_reading))

        # Test invalid reading (missing required field)
        invalid_reading = {'timestamp': datetime.now().isoformat()}
        self.assertFalse(self.power_automate._validate_reading(invalid_reading))

    def test_process_batch_readings(self):
        """Test batch processing of readings"""
        batch_readings = [
            self.test_reading,
            {
                'timestamp': datetime.now().isoformat(),
                'reading': 26.0,
                'status': 'warning'
            }
        ]

        with patch.object(self.power_automate, 'send_reading') as mock_send:
            mock_send.return_value = True
            results = self.power_automate.process_batch_readings(batch_readings)
            self.assertEqual(len(results), 2)
            self.assertTrue(all(results))

    @patch('requests.post')
    def test_retry_mechanism(self, mock_post):
        """Test retry mechanism for failed requests"""
        # Setup mock to fail first, succeed second
        mock_responses = [
            MagicMock(status_code=500),
            MagicMock(status_code=202)
        ]
        mock_post.side_effect = mock_responses

        result = self.power_automate.send_reading(
            self.test_reading, 
            max_retries=2
        )
        self.assertTrue(result)
        self.assertEqual(mock_post.call_count, 2)

if __name__ == '__main__':
    unittest.main() 