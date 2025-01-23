import pytest
import asyncio

# Set default event loop policy
@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

# Configure asyncio marker
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "asyncio: mark test as an asyncio coroutine"
    ) 