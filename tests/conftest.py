"""
Pytest configuration and fixtures for OC-Memory tests
Shared fixtures and configuration for all test modules
"""

import pytest
import tempfile
from pathlib import Path
import yaml


@pytest.fixture(scope="session")
def test_data_dir():
    """Get the test data directory"""
    return Path(__file__).parent / "data"


@pytest.fixture
def sample_yaml_config():
    """Sample YAML configuration for testing"""
    return {
        'watch': {
            'dirs': ['~/Documents/notes', '~/Projects'],
            'recursive': True,
            'poll_interval': 1.0
        },
        'memory': {
            'dir': '~/.openclaw/workspace/memory',
            'auto_categorize': True,
            'max_file_size': 5242880
        },
        'logging': {
            'level': 'INFO',
            'file': 'oc-memory.log',
            'console': True
        },
        'hot_memory': {
            'ttl_days': 90,
            'max_observations': 10000
        },
        'llm': {
            'provider': 'openai',
            'model': 'gpt-4o-mini',
            'enabled': False
        },
        'obsidian': {
            'enabled': False
        },
        'dropbox': {
            'enabled': False
        }
    }


@pytest.fixture
def temp_yaml_file(sample_yaml_config):
    """Create a temporary YAML file with sample config"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(sample_yaml_config, f)
        temp_path = f.name

    yield temp_path

    # Cleanup
    Path(temp_path).unlink()


@pytest.fixture
def temp_markdown_file():
    """Create a temporary markdown file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write("""# Test Document

## Section 1
Content for section 1

## Section 2
Content for section 2
""")
        temp_path = f.name

    yield Path(temp_path)

    # Cleanup
    Path(temp_path).unlink()


@pytest.fixture
def temp_directory():
    """Create a temporary directory"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def nested_directory():
    """Create a nested directory structure"""
    with tempfile.TemporaryDirectory() as temp_dir:
        base = Path(temp_dir)
        (base / 'level1').mkdir()
        (base / 'level1' / 'level2').mkdir()
        (base / 'level1' / 'level2' / 'level3').mkdir()
        yield base


def pytest_configure(config):
    """Configure pytest plugins and markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Mark integration tests
        if "integration" in item.nodeid.lower():
            item.add_marker(pytest.mark.integration)

        # Mark slow tests
        if item.get_closest_marker("slow"):
            pass  # Already marked

        # Mark by module
        if "config" in item.nodeid:
            item.add_marker(pytest.mark.config)
        elif "file_watcher" in item.nodeid:
            item.add_marker(pytest.mark.file_watcher)
        elif "memory_writer" in item.nodeid:
            item.add_marker(pytest.mark.memory_writer)
