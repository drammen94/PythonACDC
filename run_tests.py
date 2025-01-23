import pytest
import os
import sys

def run_tests():
    # Test files to run
    test_files = [
        'test_sensor.py',
        'test_voice.py',
        'test_powerautomate.py',
        'test_integration.py'
    ]
    
    # Basic pytest arguments with async support
    pytest_args = [
        '-v',
        '--asyncio-mode=auto',
        '--capture=no',
        '--cov=.',
        '--cov-report=term-missing',
        '--cov-config=.coveragerc'
    ]
    
    # Try to add coverage reporting if plugin is available
    try:
        import pytest_cov
        pytest_args.extend(['--cov=.', '--cov-report=term-missing'])
    except ImportError:
        print("Coverage reporting disabled: pytest-cov not installed")
    
    # Add test files to arguments
    pytest_args.extend(test_files)

    # Run tests
    result = pytest.main(pytest_args)
    
    # Return 0 for success, 1 for failures
    return 0 if result == 0 else 1

if __name__ == '__main__':
    sys.exit(run_tests())