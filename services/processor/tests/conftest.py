"""
Pytest configuration for News Feed Engine tests.
This file ensures proper Python path setup.
"""
import os
import sys

# Add the processor directory to the Python path
processor_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if processor_dir not in sys.path:
    sys.path.insert(0, processor_dir)


def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")


# Pre-import processor.main to register Prometheus metrics once
# This avoids "Duplicated timeseries" errors in tests
try:
    from data.processors import main as _main_module
except (ImportError, ValueError):
    _main_module = None
"""
Pytest configuration for News Feed Engine tests.
This file ensures proper Python path setup.
"""
import os
import sys

# Add the processor directory to the Python path
processor_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if processor_dir not in sys.path:
    sys.path.insert(0, processor_dir)

# Configure pytest-asyncio
pytest_plugins = ["pytest_asyncio"]


def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow running tests")
    config.addinivalue_line("markers", "e2e: End-to-end tests")


# Pre-import processor.main to register Prometheus metrics once
# This avoids "Duplicated timeseries" errors in tests
try:
    from data.processors import main as _main_module
except (ImportError, ValueError):
    """
    Pytest configuration for News Feed Engine tests.
    This file ensures proper Python path setup.
    """
    import os
    import sys

    # Add the processor directory to the Python path
    processor_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if processor_dir not in sys.path:
        sys.path.insert(0, processor_dir)

    def pytest_configure(config):
        """Configure custom pytest markers."""
        config.addinivalue_line("markers", "unit: Unit tests")
        config.addinivalue_line("markers", "integration: Integration tests")
        config.addinivalue_line("markers", "slow: Slow running tests")
        config.addinivalue_line("markers", "e2e: End-to-end tests")

    # Pre-import processor.main to register Prometheus metrics once
    # This avoids "Duplicated timeseries" errors in tests
    try:
        from data.processors import main as _main_module
    except (ImportError, ValueError):
        _main_module = None
