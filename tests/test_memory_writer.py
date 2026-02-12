"""
Unit tests for lib/memory_writer.py
Tests memory file writing, metadata handling, and categorization
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime
from lib.memory_writer import (
    MemoryWriterError,
    MemoryWriter
)


@pytest.fixture
def temp_memory_dir():
    """Create a temporary memory directory"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def memory_writer(temp_memory_dir):
    """Create a MemoryWriter instance"""
    return MemoryWriter(str(temp_memory_dir))


@pytest.fixture
def sample_markdown_file(temp_memory_dir):
    """Create a sample markdown file to copy"""
    source_dir = temp_memory_dir / 'source'
    source_dir.mkdir()
    test_file = source_dir / 'test_note.md'
    test_file.write_text('# Test Note\n\n## Content\nTest content here.')
    return test_file


class TestMemoryWriterInit:
    """Tests for MemoryWriter initialization"""

    def test_init_creates_directory(self):
        """Test that __init__ creates memory directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            memory_path = Path(temp_dir) / 'new_memory'
            assert not memory_path.exists()

            writer = MemoryWriter(str(memory_path))

            assert memory_path.exists()

    def test_init_with_existing_directory(self, temp_memory_dir):
        """Test initialization with existing directory"""
        writer = MemoryWriter(str(temp_memory_dir))
        # Use resolve() for comparison to handle symlinks consistently
        assert writer.memory_dir == temp_memory_dir.resolve()

    def test_init_expands_home_path(self):
        """Test that ~ is expanded in memory directory path"""
        writer = MemoryWriter('~/.openclaw/test_memory')
        home = str(Path.home())
        assert str(writer.memory_dir).startswith(home)

    def test_init_sets_logger(self, temp_memory_dir):
        """Test that logger is initialized"""
        writer = MemoryWriter(str(temp_memory_dir))
        assert writer.logger is not None


class TestCopyToMemory:
    """Tests for copy_to_memory method"""

    def test_copy_simple_file(self, memory_writer, sample_markdown_file):
        """Test copying a simple file to memory"""
        result = memory_writer.copy_to_memory(sample_markdown_file)

        assert result.exists()
        assert result.name == sample_markdown_file.name
        assert result.read_text() == sample_markdown_file.read_text()

    def test_copy_with_category(self, memory_writer, sample_markdown_file):
        """Test copying file to category subdirectory"""
        result = memory_writer.copy_to_memory(
            sample_markdown_file,
            category='projects'
        )

        assert result.exists()
        assert 'projects' in str(result)
        assert result.parent.name == 'projects'

    def test_copy_preserves_metadata(self, memory_writer, sample_markdown_file):
        """Test that file metadata is preserved"""
        original_stat = sample_markdown_file.stat()

        result = memory_writer.copy_to_memory(
            sample_markdown_file,
            preserve_metadata=True
        )

        result_stat = result.stat()
        # Timestamps might not be exactly equal due to system precision
        assert abs(result_stat.st_mtime - original_stat.st_mtime) < 1

    def test_copy_without_preserving_metadata(self, memory_writer, sample_markdown_file):
        """Test copying without preserving metadata"""
        result = memory_writer.copy_to_memory(
            sample_markdown_file,
            preserve_metadata=False
        )

        assert result.exists()
        assert result.read_text() == sample_markdown_file.read_text()

    def test_copy_nonexistent_file(self, memory_writer):
        """Test copying non-existent file raises error"""
        with pytest.raises(MemoryWriterError) as exc_info:
            memory_writer.copy_to_memory(Path('/nonexistent/file.md'))
        assert "Source file not found" in str(exc_info.value)

    def test_copy_file_conflict_resolution(self, memory_writer, sample_markdown_file):
        """Test handling of filename conflicts"""
        # First copy
        result1 = memory_writer.copy_to_memory(sample_markdown_file)

        # Second copy should have different name
        result2 = memory_writer.copy_to_memory(sample_markdown_file)

        assert result1.exists()
        assert result2.exists()
        assert result1.name != result2.name
        # Timestamp should be in the filename
        assert '_' in result2.stem


class TestWriteMemoryEntry:
    """Tests for write_memory_entry method"""

    def test_write_simple_entry(self, memory_writer):
        """Test writing a simple memory entry"""
        content = "# Test Entry\n\nSome content"
        result = memory_writer.write_memory_entry(
            content=content,
            filename='entry.md'
        )

        assert result.exists()
        assert result.read_text() == content

    def test_write_entry_with_category(self, memory_writer):
        """Test writing entry to category"""
        content = "# Categorized Entry"
        result = memory_writer.write_memory_entry(
            content=content,
            filename='entry.md',
            category='notes'
        )

        assert result.exists()
        assert 'notes' in str(result)
        assert result.parent.name == 'notes'

    def test_write_entry_creates_category_dir(self, memory_writer):
        """Test that category directory is created if needed"""
        content = "# Entry"
        category_dir = memory_writer.memory_dir / 'new_category'
        assert not category_dir.exists()

        memory_writer.write_memory_entry(
            content=content,
            filename='entry.md',
            category='new_category'
        )

        assert category_dir.exists()

    def test_write_entry_unicode_content(self, memory_writer):
        """Test writing entry with unicode content"""
        content = "# Unicode Test 🎉\n\nKorean: 테스트\nJapanese: テスト"
        result = memory_writer.write_memory_entry(
            content=content,
            filename='unicode.md'
        )

        assert result.exists()
        assert result.read_text(encoding='utf-8') == content


class TestAddMetadata:
    """Tests for add_metadata method"""

    def test_add_metadata_creates_frontmatter(self, memory_writer):
        """Test that add_metadata creates YAML frontmatter"""
        # Create a file first
        test_file = memory_writer.memory_dir / 'test.md'
        test_file.write_text('# Original Content')

        # Add metadata
        memory_writer.add_metadata(test_file, {
            'created': '2026-02-12',
            'category': 'test'
        })

        content = test_file.read_text()
        assert content.startswith('---')
        assert 'created: 2026-02-12' in content
        assert 'category: test' in content
        assert '# Original Content' in content

    def test_add_metadata_replaces_existing(self, memory_writer):
        """Test that add_metadata replaces existing frontmatter"""
        test_file = memory_writer.memory_dir / 'test.md'
        original = '---\nold: value\n---\n\nContent'
        test_file.write_text(original)

        memory_writer.add_metadata(test_file, {'new': 'value'})

        content = test_file.read_text()
        assert 'old: value' not in content
        assert 'new: value' in content

    def test_add_metadata_various_types(self, memory_writer):
        """Test adding metadata with various types"""
        test_file = memory_writer.memory_dir / 'test.md'
        test_file.write_text('Content')

        memory_writer.add_metadata(test_file, {
            'string_field': 'value',
            'int_field': 42,
            'bool_field': True,
            'list_field': ['item1', 'item2'],
            'float_field': 3.14
        })

        content = test_file.read_text()
        assert 'string_field: value' in content
        assert 'int_field: 42' in content
        assert 'bool_field: True' in content
        assert 'float_field: 3.14' in content
        assert '- item1' in content
        assert '- item2' in content

    def test_add_metadata_nonexistent_file(self, memory_writer):
        """Test adding metadata to non-existent file"""
        with pytest.raises(MemoryWriterError) as exc_info:
            memory_writer.add_metadata(
                Path('/nonexistent/file.md'),
                {'key': 'value'}
            )
        assert "File not found" in str(exc_info.value)


class TestGetCategoryFromPath:
    """Tests for get_category_from_path method"""

    def test_categorize_project_path(self, memory_writer):
        """Test categorization of project paths"""
        category = memory_writer.get_category_from_path(
            Path('~/Projects/myproject/notes.md')
        )
        assert category == 'projects'

    def test_categorize_notes_path(self, memory_writer):
        """Test categorization of notes paths"""
        category = memory_writer.get_category_from_path(
            Path('~/Documents/notes/personal.md')
        )
        assert category == 'notes'

    def test_categorize_documents_path(self, memory_writer):
        """Test categorization of documents paths"""
        category = memory_writer.get_category_from_path(
            Path('~/Documents/documentation/guide.md')
        )
        assert category == 'documents'

    def test_categorize_meeting_path(self, memory_writer):
        """Test categorization of meeting paths"""
        # Note: 'Documents' contains 'doc' so it matches documents first
        category = memory_writer.get_category_from_path(
            Path('~/meetings/2026-02-12.md')
        )
        assert category == 'meetings'

    def test_categorize_unknown_path(self, memory_writer):
        """Test categorization of unknown paths"""
        category = memory_writer.get_category_from_path(
            Path('~/Downloads/random.md')
        )
        assert category == 'general'

    def test_categorize_case_insensitive(self, memory_writer):
        """Test categorization is case-insensitive"""
        category = memory_writer.get_category_from_path(
            Path('~/PROJECTS/MyProject/notes.md')
        )
        assert category == 'projects'


class TestMemoryWriterIntegration:
    """Integration tests for MemoryWriter"""

    def test_full_workflow_copy_and_metadata(self, memory_writer, sample_markdown_file):
        """Test complete workflow: copy file, add metadata, categorize"""
        # Copy file with category
        result = memory_writer.copy_to_memory(
            sample_markdown_file,
            category='copied'
        )

        # Add metadata
        memory_writer.add_metadata(result, {
            'source': str(sample_markdown_file),
            'imported_at': datetime.now().isoformat()
        })

        # Verify result
        assert result.exists()
        content = result.read_text()
        assert '---' in content
        assert 'imported_at:' in content

    def test_multiple_files_same_category(self, memory_writer, temp_memory_dir):
        """Test creating multiple files in same category"""
        category = 'test_category'

        # Create multiple entries
        for i in range(3):
            memory_writer.write_memory_entry(
                content=f'# Entry {i}',
                filename=f'entry_{i}.md',
                category=category
            )

        # Verify all files created
        category_dir = memory_writer.memory_dir / category
        assert len(list(category_dir.glob('*.md'))) == 3

    def test_auto_categorize_workflow(self, memory_writer):
        """Test workflow with automatic categorization"""
        test_path = Path('~/Projects/MyApp/README.md')
        category = memory_writer.get_category_from_path(test_path)

        # Write entry to auto-detected category
        result = memory_writer.write_memory_entry(
            content='# Project README',
            filename='README.md',
            category=category
        )

        assert 'projects' in str(result)
