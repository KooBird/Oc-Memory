"""
Unit tests for lib/config.py
Tests YAML loading, validation, and path expansion
"""

import pytest
import tempfile
from pathlib import Path
import yaml
from lib.config import (
    ConfigError,
    load_config,
    validate_config,
    expand_paths,
    get_config
)


@pytest.fixture
def temp_config_file():
    """Create a temporary config file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        config = {
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
                'api_key_env': 'OPENAI_API_KEY',
                'enabled': False
            },
            'obsidian': {
                'enabled': False
            },
            'dropbox': {
                'enabled': False
            }
        }
        yaml.dump(config, f)
        temp_path = f.name

    yield temp_path

    # Cleanup
    Path(temp_path).unlink()


@pytest.fixture
def invalid_config_file():
    """Create an invalid config file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write("invalid yaml content: [")
        temp_path = f.name

    yield temp_path

    # Cleanup
    Path(temp_path).unlink()


class TestLoadConfig:
    """Tests for load_config function"""

    def test_load_valid_config(self, temp_config_file):
        """Test loading valid config file"""
        config = load_config(temp_config_file)
        assert 'watch' in config
        assert 'memory' in config
        assert config['watch']['recursive'] is True

    def test_load_nonexistent_config(self):
        """Test loading non-existent config file"""
        with pytest.raises(ConfigError) as exc_info:
            load_config('/path/that/does/not/exist.yaml')
        assert "Config file not found" in str(exc_info.value)

    def test_load_invalid_yaml(self, invalid_config_file):
        """Test loading invalid YAML"""
        with pytest.raises(ConfigError) as exc_info:
            load_config(invalid_config_file)
        assert "Invalid YAML" in str(exc_info.value)

    def test_load_missing_required_section(self):
        """Test loading config without required sections"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({'watch': {'dirs': []}}, f)
            temp_path = f.name

        try:
            with pytest.raises(ConfigError) as exc_info:
                load_config(temp_path)
            assert "Missing required section" in str(exc_info.value)
        finally:
            Path(temp_path).unlink()


class TestValidateConfig:
    """Tests for validate_config function"""

    def test_validate_valid_config(self, temp_config_file):
        """Test validating valid config"""
        config = load_config(temp_config_file)
        assert validate_config(config) is True

    def test_validate_missing_watch_dirs(self):
        """Test validation with missing watch.dirs"""
        config = {'watch': {}, 'memory': {'dir': '/tmp'}}
        with pytest.raises(ConfigError) as exc_info:
            validate_config(config)
        assert "Missing 'dirs'" in str(exc_info.value)

    def test_validate_invalid_watch_dirs_type(self):
        """Test validation with non-list watch.dirs"""
        config = {
            'watch': {'dirs': '/tmp'},
            'memory': {'dir': '/tmp'}
        }
        with pytest.raises(ConfigError) as exc_info:
            validate_config(config)
        assert "must be a list" in str(exc_info.value)

    def test_validate_missing_memory_dir(self):
        """Test validation with missing memory.dir"""
        config = {
            'watch': {'dirs': ['/tmp']},
            'memory': {}
        }
        with pytest.raises(ConfigError) as exc_info:
            validate_config(config)
        assert "Missing 'dir'" in str(exc_info.value)


class TestExpandPaths:
    """Tests for expand_paths function"""

    def test_expand_home_paths(self):
        """Test expanding ~ in paths"""
        config = {
            'watch': {'dirs': ['~/Documents', '~/Projects']},
            'memory': {'dir': '~/.openclaw/workspace/memory'}
        }
        expanded = expand_paths(config)

        home = str(Path.home())
        assert expanded['watch']['dirs'][0].startswith(home)
        assert expanded['memory']['dir'].startswith(home)
        assert '~' not in expanded['watch']['dirs'][0]

    def test_expand_absolute_paths(self):
        """Test that absolute paths are preserved"""
        config = {
            'watch': {'dirs': ['/tmp/notes']},
            'memory': {'dir': '/tmp/memory'}
        }
        expanded = expand_paths(config)

        assert expanded['watch']['dirs'][0] == str(Path('/tmp/notes').resolve())
        assert expanded['memory']['dir'] == str(Path('/tmp/memory').resolve())

    def test_expand_missing_sections(self):
        """Test expand_paths handles missing sections gracefully"""
        config = {}
        expanded = expand_paths(config)
        assert expanded == {}


class TestGetConfig:
    """Tests for get_config function"""

    def test_get_config_complete_flow(self, temp_config_file):
        """Test complete config loading and processing"""
        config = get_config(temp_config_file)

        # Should have expanded paths
        assert '~' not in str(config['watch']['dirs'])
        assert '~' not in config['memory']['dir']

        # Should have valid structure
        assert isinstance(config['watch']['dirs'], list)
        assert len(config['watch']['dirs']) > 0
        assert isinstance(config['memory']['dir'], str)

    def test_get_config_with_home_expansion(self, temp_config_file):
        """Test that get_config properly expands home directory"""
        config = get_config(temp_config_file)
        home = str(Path.home())

        for watch_dir in config['watch']['dirs']:
            assert watch_dir.startswith(home) or watch_dir.startswith('/')


class TestIntegration:
    """Integration tests"""

    def test_full_config_workflow(self):
        """Test complete workflow: create, load, validate, expand"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_dict = {
                'watch': {'dirs': ['~/test_notes']},
                'memory': {'dir': '~/.test_memory'}
            }
            yaml.dump(config_dict, f)
            temp_path = f.name

        try:
            # Load config
            config = load_config(temp_path)
            assert config['watch']['dirs'] == ['~/test_notes']

            # Validate
            assert validate_config(config) is True

            # Expand paths
            expanded = expand_paths(config)
            assert '~' not in expanded['watch']['dirs'][0]
            assert '~' not in expanded['memory']['dir']

        finally:
            Path(temp_path).unlink()
