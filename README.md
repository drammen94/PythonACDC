# Python Automated Control and Data Collection (ACDC) System

## Overview
This system provides an integrated solution for automated control and data collection, combining sensor readings, voice commands, and Power Automate integration. It's designed to be modular, extensible, and robust, with comprehensive test coverage.

## System Architecture

### Core Components and Interconnections

#### System Flow and Data Pipeline

1. **System Integrator (Central Hub)**
   - Acts as the orchestration layer connecting all components
   - Data flow:
     ```
     Sensor → Integrator → Power Automate + WebSocket
     Voice → Integrator → Potion Mixer → Power Automate
     ```
   - Maintains state and coordinates async operations
   - Implements event-driven architecture for real-time updates

2. **Component Interactions**

   a. **Sensor → Integrator**
   ```python
   # Sensor provides filtered readings
   reading = sensor.get_filtered_reading()
   # Integrator processes and broadcasts
   await manager.broadcast({
       'type': 'sensor_reading',
       'value': reading,
       'timestamp': datetime.now().isoformat()
   })
   ```

   b. **Voice → Integrator → Potion Mixer**
   ```python
   # Voice recognition flow
   command = voice_recognizer.listen_for_command()
   if 'start_potion' in command:
       await potion_mixer.start_new_potion()
   elif 'add_ingredient' in command:
       await potion_mixer.add_ingredient(ingredient_type)
   ```

   c. **Integrator → Power Automate**
   ```python
   # Data transmission to Power Automate
   self.power_automate.send_sensor_data(reading)
   self.power_automate.send_command(command)
   ```

3. **Real-time Communication Layer**
   - WebSocket server maintains live connections
   - Broadcasts updates to all connected clients
   - Supports bidirectional communication:
     ```
     Sensor Data → WebSocket → Client
     Client Command → WebSocket → System
     ```

### Data Flow Sequence

1. **Sensor Reading Pipeline**
   ```mermaid
   sequenceDiagram
       Sensor->>Integrator: Raw Reading
       Integrator->>Sensor: Request Filtered Data
       Sensor->>Integrator: Filtered Reading
       Integrator->>PowerAutomate: Send Data
       Integrator->>WebSocket: Broadcast Update
   ```

2. **Voice Command Pipeline**
   ```mermaid
   sequenceDiagram
       VoiceRecognizer->>Integrator: Audio Command
       Integrator->>VoiceRecognizer: Parse Command
       VoiceRecognizer->>Integrator: Parsed Command
       Integrator->>PotionMixer: Execute Action
       PotionMixer->>PowerAutomate: Status Update
   ```

### State Management

1. **Component States**
   - Sensor: Maintains reading history and calibration state
   - Voice Recognizer: Tracks command context and session state
   - Potion Mixer: Manages current potion state and ingredient tracking
   - Integrator: Orchestrates overall system state

2. **State Synchronization**
   ```python
   class SystemIntegrator:
       async def run_monitoring_cycle(self):
           # Synchronize states
           sensor_state = await self.process_sensor_reading()
           voice_state = await self.process_voice_command()
           
           # Update global state
           self.update_system_state(sensor_state, voice_state)
           
           # Broadcast state changes
           await self.broadcast_state_update()
   ```

### Error Handling and Recovery

1. **Component-Level Recovery**
   ```python
   try:
       reading = self.sensor.get_filtered_reading()
   except SensorError:
       # Component-level recovery
       self.sensor.recalibrate()
       reading = self.sensor.get_filtered_reading()
   ```

2. **System-Level Recovery**
   ```python
   async def handle_component_failure(self, component):
       # Log failure
       logging.error(f"{component} failure detected")
       
       # Attempt recovery
       if await self.recover_component(component):
           # Resume operations
           await self.resume_monitoring()
       else:
           # Fallback mode
           await self.enter_fallback_mode()
   ```

### Testing Integration

1. **Mock Interaction Testing**
   ```python
   async def test_component_interaction(self):
       # Setup component mocks
       self.mock_sensor.get_filtered_reading.return_value = 25.5
       self.mock_voice.listen_for_command.return_value = ["start_potion"]
       
       # Test interaction flow
       result = await self.integrator.process_all_components()
       assert result['sensor_success'] and result['voice_success']
   ```

2. **Async Operation Testing**
   ```python
   class AsyncMock(MagicMock):
       async def __call__(self, *args, **kwargs):
           return super(AsyncMock, self).__call__(*args, **kwargs)
           
   # Test async component interaction
   async def test_async_flow(self):
       mock_potion_mixer = AsyncMock()
       mock_potion_mixer.start_new_potion = AsyncMock(return_value=True)
       # Test async operations
   ```

### Core Components

1. **System Integrator**
   - Central orchestrator that coordinates between all components
   - Handles sensor readings, voice commands, and automation tasks
   - Manages the potion mixing subsystem
   - Provides WebSocket broadcasting for real-time updates

2. **Liquid Level Sensor**
   - Interfaces with hardware sensors
   - Provides filtered readings
   - Implements reading storage and data validation
   - Uses GPIO for hardware communication

3. **Voice Command Recognizer**
   - Processes audio input for command recognition
   - Supports multiple command types (start_potion, add_ingredient, complete_potion)
   - Uses OpenAI's API for speech-to-text conversion
   - Implements command parsing and keyword matching

4. **Power Automate Connector**
   - Handles communication with Microsoft Power Automate
   - Manages sensor data transmission
   - Implements retry mechanisms for reliability
   - Supports batch processing of readings

### Additional Features

- **WebSocket Server**: Provides real-time data broadcasting
- **Potion Mixer**: Optional module for specialized mixing operations
- **Environment Configuration**: Uses .env for secure configuration management

## Testing Framework

### Test Structure

```python
@pytest.mark.asyncio
class TestSystemIntegration:
    @pytest.fixture(autouse=True)
    async def setup(self):
        # Setup test environment with mocks
        # Initialize system components
        # Configure test data
```

### Key Testing Features

1. **Async Testing Support**
   - Uses pytest-asyncio for handling asynchronous operations
   - Custom AsyncMock implementation for mocking async methods:
   ```python
   class AsyncMock(MagicMock):
       async def __call__(self, *args, **kwargs):
           return super(AsyncMock, self).__call__(*args, **kwargs)
   ```

2. **Component Mocking**
   - Mocks for hardware dependencies (sensors, GPIO)
   - Voice recognition service mocking
   - Power Automate endpoint simulation

3. **Test Coverage**
   - Sensor reading processing
   - Voice command handling
   - Integration with Power Automate
   - Error handling and logging
   - Full monitoring cycle validation

### Test Cases

1. **Sensor Operations**
   - Filtered reading validation
   - Reading storage
   - Sensor initialization

2. **Voice Command Processing**
   - Command recognition
   - Keyword matching
   - Audio processing
   - Command parsing

3. **Power Automate Integration**
   - Data transmission
   - Batch processing
   - Retry mechanism
   - Reading validation

4. **System Integration**
   - End-to-end monitoring cycles
   - Error handling
   - Component interaction
   - Resource cleanup

## Setup and Usage

### Prerequisites
- Python 3.11+
- Required packages (install via pip):
  ```
  pytest
  pytest-asyncio
  pytest-cov
  ```

### Environment Configuration
Create a `.env` file with:
```
OPENAI_API_KEY=your_api_key
POWER_AUTOMATE_SENSOR_ENDPOINT=your_sensor_endpoint
POWER_AUTOMATE_COMMAND_ENDPOINT=your_command_endpoint
```

### Running Tests
```bash
python run_tests.py
```

This will execute all test cases with coverage reporting.

## Development Guidelines

### Adding New Features
1. Create new component module
2. Add corresponding test file
3. Update integration_script.py if needed
4. Add tests to run_tests.py

### Testing Best Practices
1. Use async/await properly for asynchronous operations
2. Implement proper mocking for external dependencies
3. Ensure comprehensive error handling
4. Maintain high test coverage

### Error Handling
- All components implement robust error handling
- Errors are logged with appropriate context
- Failed operations are gracefully handled
- System maintains stability during component failures

## Troubleshooting

### Common Issues
1. **Async Operation Errors**
   - Ensure proper use of async/await
   - Check mock implementations for async methods
   - Verify event loop handling

2. **Mock Configuration**
   - Verify mock return values
   - Check mock method signatures
   - Ensure proper async mock setup

3. **Integration Issues**
   - Verify environment variables
   - Check endpoint configurations
   - Validate component initialization

## Contributing
1. Fork the repository
2. Create feature branch
3. Implement changes with tests
4. Submit pull request with documentation

## License
[MIT License](LICENSE) 