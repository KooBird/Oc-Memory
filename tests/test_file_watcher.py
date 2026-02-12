"""
Unit tests for lib/file_watcher.py
Tests markdown file detection and event handling
"""

import pytest
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch
from lib.file_watcher import (
    MarkdownFileHandler,
    FileWatcher
)


@pytest.fixture
def temp_watch_dir():
    """Create a temporary directory for watching"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_callback():
    """Create a mock callback function"""
    return Mock()


class TestMarkdownFileHandler:
    """Tests for MarkdownFileHandler class"""

    def test_init_with_callback(self, mock_callback):
        """Test initialization with callback"""
        handler = MarkdownFileHandler(callback=mock_callback)
        assert handler.callback == mock_callback

    def test_init_without_callback(self):
        """Test initialization without callback"""
        handler = MarkdownFileHandler()
        assert handler.callback is None

    def test_is_markdown_file_md_extension(self, mock_callback):
        """Test markdown file detection for .md files"""
        handler = MarkdownFileHandler(callback=mock_callback)
        assert handler._is_markdown_file('/path/to/file.md') is True

    def test_is_markdown_file_markdown_extension(self, mock_callback):
        """Test markdown file detection for .markdown files"""
        handler = MarkdownFileHandler(callback=mock_callback)
        assert handler._is_markdown_file('/path/to/file.markdown') is True

    def test_is_markdown_file_non_markdown(self, mock_callback):
        """Test markdown file detection for non-markdown files"""
        handler = MarkdownFileHandler(callback=mock_callback)
        assert handler._is_markdown_file('/path/to/file.txt') is False
        assert handler._is_markdown_file('/path/to/file.py') is False
        assert handler._is_markdown_file('/path/to/file.pdf') is False

    def test_is_markdown_file_case_insensitive(self, mock_callback):
        """Test markdown file detection is case-insensitive"""
        handler = MarkdownFileHandler(callback=mock_callback)
        assert handler._is_markdown_file('/path/to/file.MD') is True
        assert handler._is_markdown_file('/path/to/file.Md') is True
        assert handler._is_markdown_file('/path/to/file.MARKDOWN') is True

    def test_on_created_markdown_file(self, temp_watch_dir, mock_callback):
        """Test creation event for markdown file"""
        handler = MarkdownFileHandler(callback=mock_callback)

        # Create a mock event
        test_file = temp_watch_dir / 'test.md'
        test_file.touch()

        from watchdog.events import FileCreatedEvent
        event = FileCreatedEvent(str(test_file))

        # Handle the event
        handler.on_created(event)

        # Callback should have been called
        assert mock_callback.called

    def test_on_created_non_markdown_file(self, temp_watch_dir, mock_callback):
        """Test creation event for non-markdown file"""
        handler = MarkdownFileHandler(callback=mock_callback)

        test_file = temp_watch_dir / 'test.txt'
        test_file.touch()

        from watchdog.events import FileCreatedEvent
        event = FileCreatedEvent(str(test_file))

        handler.on_created(event)

        # Callback should NOT have been called
        assert not mock_callback.called

    def test_on_created_directory_ignored(self, temp_watch_dir, mock_callback):
        """Test that directory creation events are ignored"""
        handler = MarkdownFileHandler(callback=mock_callback)

        test_dir = temp_watch_dir / 'subdir'
        test_dir.mkdir()

        from watchdog.events import DirCreatedEvent
        event = DirCreatedEvent(str(test_dir))

        handler.on_created(event)

        # Callback should NOT have been called
        assert not mock_callback.called

    def test_on_modified_markdown_file(self, temp_watch_dir, mock_callback):
        """Test modification event for markdown file"""
        handler = MarkdownFileHandler(callback=mock_callback)

        test_file = temp_watch_dir / 'test.md'
        test_file.write_text('# Test')

        from watchdog.events import FileModifiedEvent
        event = FileModifiedEvent(str(test_file))

        handler.on_modified(event)

        # Callback should have been called
        assert mock_callback.called

    def test_callback_receives_correct_arguments(self, temp_watch_dir, mock_callback):
        """Test that callback receives correct arguments"""
        handler = MarkdownFileHandler(callback=mock_callback)

        test_file = temp_watch_dir / 'test.md'
        test_file.touch()

        from watchdog.events import FileCreatedEvent
        event = FileCreatedEvent(str(test_file))

        handler.on_created(event)

        # Check callback was called with correct arguments
        mock_callback.assert_called_once()
        args, kwargs = mock_callback.call_args
        # Callback is called with positional args
        assert isinstance(args[0], Path)
        assert kwargs.get('event_type') == 'created' or (len(args) > 1 and args[1] == 'created')


class TestFileWatcher:
    """Tests for FileWatcher class"""

    def test_init_basic(self, temp_watch_dir):
        """Test basic initialization"""
        watcher = FileWatcher(watch_dirs=[str(temp_watch_dir)])
        assert len(watcher.watch_dirs) == 1
        assert watcher.recursive is True

    def test_init_multiple_dirs(self, temp_watch_dir):
        """Test initialization with multiple directories"""
        dir1 = temp_watch_dir / 'dir1'
        dir2 = temp_watch_dir / 'dir2'
        dir1.mkdir()
        dir2.mkdir()

        watcher = FileWatcher(watch_dirs=[str(dir1), str(dir2)])
        assert len(watcher.watch_dirs) == 2

    def test_init_with_callback(self, temp_watch_dir, mock_callback):
        """Test initialization with callback"""
        watcher = FileWatcher(
            watch_dirs=[str(temp_watch_dir)],
            callback=mock_callback
        )
        assert watcher.callback == mock_callback

    def test_init_recursive_true(self, temp_watch_dir):
        """Test initialization with recursive=True"""
        watcher = FileWatcher(watch_dirs=[str(temp_watch_dir)], recursive=True)
        assert watcher.recursive is True

    def test_init_recursive_false(self, temp_watch_dir):
        """Test initialization with recursive=False"""
        watcher = FileWatcher(watch_dirs=[str(temp_watch_dir)], recursive=False)
        assert watcher.recursive is False

    def test_init_with_nonexistent_dir(self):
        """Test initialization with non-existent directory"""
        watcher = FileWatcher(watch_dirs=['/path/that/does/not/exist'])
        # Should not raise, but log a warning
        assert len(watcher.watch_dirs) == 1

    def test_init_expands_home_paths(self):
        """Test that ~ paths are expanded"""
        watcher = FileWatcher(watch_dirs=['~/test_notes'])
        home = str(Path.home())
        assert str(watcher.watch_dirs[0]).startswith(home)

    def test_start_stop_basic(self, temp_watch_dir):
        """Test starting and stopping watcher"""
        watcher = FileWatcher(watch_dirs=[str(temp_watch_dir)])

        watcher.start()
        assert watcher.is_alive() is True

        watcher.stop()
        # Give it a moment to stop
        time.sleep(0.1)

    def test_is_alive_before_start(self, temp_watch_dir):
        """Test is_alive returns False before start"""
        watcher = FileWatcher(watch_dirs=[str(temp_watch_dir)])
        assert watcher.is_alive() is False

    def test_start_with_nonexistent_dir(self):
        """Test starting watcher with non-existent directory"""
        watcher = FileWatcher(watch_dirs=['/path/that/does/not/exist'])
        # Should not raise an error
        watcher.start()
        assert watcher.is_alive() is True
        watcher.stop()

    def test_observer_created_on_init(self, temp_watch_dir):
        """Test that Observer is created during initialization"""
        watcher = FileWatcher(watch_dirs=[str(temp_watch_dir)])
        assert watcher.observer is not None
        from watchdog.observers import Observer
        assert isinstance(watcher.observer, Observer)


class TestFileWatcherIntegration:
    """Integration tests for FileWatcher"""

    def test_watch_markdown_file_creation(self, temp_watch_dir):
        """Test watching for markdown file creation"""
        callback = Mock()
        watcher = FileWatcher(
            watch_dirs=[str(temp_watch_dir)],
            callback=callback,
            recursive=True
        )

        watcher.start()

        # Create a markdown file
        test_file = temp_watch_dir / 'test.md'
        test_file.write_text('# Test Note')

        # Wait for event to be processed
        time.sleep(0.5)

        watcher.stop()

        # Callback should have been called
        assert callback.called

    def test_watch_non_markdown_file_ignored(self, temp_watch_dir):
        """Test that non-markdown files are ignored"""
        callback = Mock()
        watcher = FileWatcher(
            watch_dirs=[str(temp_watch_dir)],
            callback=callback
        )

        watcher.start()

        # Create a non-markdown file
        test_file = temp_watch_dir / 'test.txt'
        test_file.write_text('text content')

        # Wait for event to be processed
        time.sleep(0.5)

        watcher.stop()

        # Callback should NOT have been called
        assert not callback.called

    def test_recursive_watching(self, temp_watch_dir):
        """Test recursive watching in subdirectories"""
        callback = Mock()
        watcher = FileWatcher(
            watch_dirs=[str(temp_watch_dir)],
            callback=callback,
            recursive=True
        )

        watcher.start()

        # Create nested directories and file
        subdir = temp_watch_dir / 'subdir' / 'nested'
        subdir.mkdir(parents=True)
        test_file = subdir / 'test.md'
        test_file.write_text('# Nested Note')

        # Wait for event to be processed
        time.sleep(0.5)

        watcher.stop()

        # Callback should have been called
        assert callback.called
