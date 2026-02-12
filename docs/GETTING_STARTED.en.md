# Getting Started with OC-Memory

Get up and running with OC-Memory in under 5 minutes! This guide covers installation, configuration, running the system, and troubleshooting.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.10 or higher** - Check with: `python3 --version`
  - Supported versions: 3.10, 3.11, 3.12, 3.14
  - Python 3.14 users: chromadb automatically excluded (uses OpenClaw built-in search)
  - ⚠️ Important: Python 3.9 and below are not supported
- **pip** - Included with Python 3.9+
- **Virtual environment** (recommended) - Built into Python
  ```bash
  python3 -m venv venv
  source venv/bin/activate    # macOS/Linux
  # or
  venv\Scripts\activate       # Windows
  ```
- **Disk space** - At least 100MB free for dependencies and logs
- **OpenClaw installed** - Required for memory integration (see [OpenClaw Repository](https://github.com/openclaw-ai/openclaw))

### System Requirements

- **Linux/macOS/Windows** - All supported
- **Disk I/O** - Good performance for file watching (SSD recommended but not required)
- **Network** - Optional for API features (basic operation works offline)

---

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/openclaw-ai/oc-memory.git
cd oc-memory
```

### Step 2: Create and Activate Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate          # On macOS/Linux
# OR
venv\Scripts\activate             # On Windows
```

You should see `(venv)` at the start of your terminal prompt.

### Step 3: Install Dependencies

```bash
# Make sure virtual environment is active (you should see (venv) in your prompt)
pip install -r requirements.txt
```

This installs all required packages including `watchdog` (file monitoring), `pyyaml` (configuration), and others.

**v0.2.1 Changes:**
- ❌ chromadb removed (Python 3.14 compatibility)
- ✅ Uses OpenClaw built-in SQLite vector search
- 📦 49 packages total (fewer than before)

### Step 4: Verify Installation

```bash
python -c "import watchdog; import yaml; print('✅ Installation successful')"
```

---

## Understanding the Setup

### What Gets Configured

During setup, OC-Memory configures:

1. **Watch Directories** - Directories to monitor for `.md` files
   - Default: `~/Documents/notes`, `~/Projects`
   - Can be customized to monitor any directories

2. **Memory Directory** - Where synchronized files are stored
   - Default: `~/.openclaw/workspace/memory`
   - This is OpenClaw's built-in memory system

3. **Logging** - Debug/info logging to track what's happening
   - Log file: `oc-memory.log`
   - Can be set to DEBUG for troubleshooting

4. **Auto-categorization** - Automatic sorting of files into categories
   - `notes/` - Files from note directories
   - `projects/` - Files from project directories
   - `documents/` - Files from document directories
   - `general/` - Uncategorized files

### Default Configuration

The default `config.yaml` looks like:

```yaml
watch:
  dirs:
    - ~/Documents/notes
    - ~/Projects
  recursive: true              # Watch subdirectories

memory:
  dir: ~/.openclaw/workspace/memory
  auto_categorize: true        # Enable category detection

logging:
  level: INFO                  # DEBUG, INFO, WARNING, ERROR
  file: oc-memory.log
  console: true                # Show output while running
```

### Customizing Your Configuration

To modify the configuration:

```bash
# Edit the config file
nano config.yaml    # or use your preferred editor
```

Common customizations:

```yaml
# Add more watch directories
watch:
  dirs:
    - ~/Documents/notes
    - ~/Projects
    - ~/Desktop/scratch
    - ~/my-notes

# Change memory directory if needed
memory:
  dir: ~/.openclaw/workspace/memory
  auto_categorize: true

# Enable verbose logging for troubleshooting
logging:
  level: DEBUG
  file: oc-memory.log
  console: true
```

---

## First Run

### Starting the Memory Observer

The memory observer is the main daemon process that monitors your directories and syncs files to OpenClaw:

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Start the observer
python memory_observer.py
```

You should see output like:

```
2026-02-12 10:30:45,123 - memory_observer - INFO - ============================================================
2026-02-12 10:30:45,124 - memory_observer - INFO - Starting OC-Memory Observer
2026-02-12 10:30:45,125 - memory_observer - INFO - ============================================================
2026-02-12 10:30:45,126 - memory_observer - INFO - Watch directories: ['/Users/your-username/Documents/notes', ...]
2026-02-12 10:30:45,127 - memory_observer - INFO - Memory directory: /Users/your-username/.openclaw/workspace/memory
2026-02-12 10:30:45,128 - memory_observer - INFO - ============================================================
2026-02-12 10:30:45,129 - memory_observer - INFO - OC-Memory Observer started successfully
2026-02-12 10:30:45,130 - memory_observer - INFO - Monitoring for file changes... (Press Ctrl+C to stop)
```

The observer is now running and monitoring your configured directories. It will remain in the foreground; you can stop it with Ctrl+C.

### What Happens When It Runs

The observer:
1. Monitors all configured watch directories for new/modified `.md` files
2. Detects file changes in real-time (1-2 second latency)
3. Copies files to OpenClaw's memory directory
4. Auto-detects and assigns categories based on file path
5. Adds metadata (timestamps, source path, category)
6. OpenClaw auto-indexes these files within ~5 seconds

---

## Understanding Each Component

### FileWatcher

**What it does:** Monitors directories for markdown file changes

- Watches one or more directories recursively
- Detects when `.md` files are created or modified
- Ignores non-markdown files
- Triggers a callback function when changes are detected
- Uses the `watchdog` library for cross-platform file monitoring

**Location:** `lib/file_watcher.py`

**How to test it manually:**

```bash
python << 'EOF'
from lib.file_watcher import FileWatcher
import time

def on_change(file_path, event_type):
    print(f"[{event_type.upper()}] {file_path}")

watcher = FileWatcher(
    watch_dirs=['~/Documents/notes'],
    callback=on_change
)

print("Starting FileWatcher. Modify .md files to test...")
watcher.start()

try:
    for i in range(30):
        time.sleep(1)
except KeyboardInterrupt:
    pass

watcher.stop()
EOF
```

### MemoryWriter

**What it does:** Writes files to OpenClaw's memory system with metadata

Core functions:
- **copy_to_memory()** - Copies file to memory directory, handles conflicts
- **write_memory_entry()** - Creates new memory entries from content
- **add_metadata()** - Adds YAML frontmatter with timestamps, category, source path
- **get_category_from_path()** - Auto-detects category from file path

**Location:** `lib/memory_writer.py`

**How it categorizes files:**
- Path contains "project" → `projects/` folder
- Path contains "note" → `notes/` folder
- Path contains "doc" or "document" → `documents/` folder
- Path contains "meeting" → `meetings/` folder
- Everything else → `general/` folder

**How to test it manually:**

```bash
python << 'EOF'
from lib.memory_writer import MemoryWriter
from pathlib import Path
from datetime import datetime

writer = MemoryWriter('~/.openclaw/workspace/memory')

# Create a test file
test_file = Path('~/Documents/notes/test.md').expanduser()
test_file.write_text("# Test Note\nThis is a test.")

# Copy to memory
category = writer.get_category_from_path(test_file)
target = writer.copy_to_memory(test_file, category=category)

# Add metadata
writer.add_metadata(target, {
    'source': str(test_file),
    'synced_at': datetime.now().isoformat(),
    'category': category
})

print(f"✅ File synced to: {target}")
EOF
```

### Memory Observer Daemon

**What it does:** Orchestrates FileWatcher and MemoryWriter components

The main `memory_observer.py` process:
1. Loads configuration from `config.yaml`
2. Initializes FileWatcher with configured directories
3. Initializes MemoryWriter with memory directory
4. Starts FileWatcher and waits for file change events
5. When a file changes, automatically syncs it to memory
6. Tracks statistics (files processed, errors)
7. Gracefully handles shutdown (Ctrl+C)

**Flow diagram:**

```
User creates/edits .md file
          ↓
FileWatcher detects change
          ↓
FileWatcher triggers callback
          ↓
memory_observer processes file
          ↓
MemoryWriter copies to memory directory
          ↓
MemoryWriter adds metadata (timestamp, category, source)
          ↓
OpenClaw auto-indexes the file (~5 seconds)
          ↓
Memory is searchable in OpenClaw
```

---

## What Happens Automatically

### File Detection

When you create or modify a `.md` file in a watched directory:

1. FileWatcher detects the change within 1-2 seconds
2. Logs the detection: `New markdown file detected: /path/to/file.md`
3. Triggers the sync process

### Category Detection

OC-Memory automatically detects file category from the file path:

```
~/Documents/notes/python-tips.md     → notes/
~/Projects/ai-research/summary.md    → projects/
~/Documents/meeting-notes.md         → documents/
~/misc/article.md                    → general/
```

### Metadata Addition

Every synced file gets YAML frontmatter with:

```yaml
---
source: /Users/you/Documents/notes/example.md
synced_at: 2026-02-12T10:30:47.123456
category: notes
event_type: created
oc_memory_version: 0.1.0
---

# Original file content here...
```

### OpenClaw Integration

After a file is synced:
1. File appears in `~/.openclaw/workspace/memory/[category]/`
2. OpenClaw's file watcher detects the new file
3. OpenClaw auto-indexes it (~5 seconds)
4. File is searchable via OpenClaw's memory_search tool

---

## Verification

### How to Verify Basic Operation

Follow these steps to confirm everything is working:

#### Terminal 1: Start the Observer

```bash
source venv/bin/activate
python memory_observer.py
```

Leave this running.

#### Terminal 2: Create a Test Note

```bash
# Create the notes directory if it doesn't exist
mkdir -p ~/Documents/notes

# Create a test note
cat > ~/Documents/notes/test_note.md << 'EOF'
# Test Memory Entry

This is a test note for OC-Memory verification.

## Key Points
- First point
- Second point
EOF
```

#### Expected Behavior

In Terminal 1, you should see:

```
2026-02-12 10:32:15,456 - lib.file_watcher - INFO - New markdown file detected: /Users/you/Documents/notes/test_note.md
2026-02-12 10:32:15,457 - memory_observer - INFO - Processing file: /Users/you/Documents/notes/test_note.md (created)
2026-02-12 10:32:15,458 - memory_observer - INFO - Synced to memory: /Users/you/.openclaw/workspace/memory/notes/test_note.md (total: 1)
```

#### Check the Memory Directory

```bash
# List synchronized files
ls -la ~/.openclaw/workspace/memory/notes/

# View the synced file with metadata
cat ~/.openclaw/workspace/memory/notes/test_note.md
```

You should see the file with YAML frontmatter added.

---

## Testing With Your Own Files

### Quick Test (2 minutes)

```bash
# In Terminal 2, while observer is running:

# Create a new note
echo "# My Project Notes" > ~/Documents/notes/project.md
echo "Important details here" >> ~/Documents/notes/project.md

# Wait 2 seconds
sleep 2

# Check if it was synced
ls -la ~/.openclaw/workspace/memory/notes/
```

### Comprehensive Test (10 minutes)

Create multiple files in different directories to test categorization:

```bash
# Create test files
mkdir -p ~/Documents/notes
mkdir -p ~/Projects/demo
mkdir -p ~/Documents/research

# Notes
echo "# Note 1" > ~/Documents/notes/note1.md
echo "# Note 2" > ~/Documents/notes/sub/note2.md

# Projects
echo "# Project Update" > ~/Projects/demo/status.md

# Documents
echo "# Research" > ~/Documents/research/paper.md

# Check results after 5 seconds
sleep 5
find ~/.openclaw/workspace/memory -name "*.md" -type f
```

You should see files organized into their respective categories.

---

## Monitoring Logs

### View Recent Logs

```bash
# Last 50 lines
tail -50 oc-memory.log

# Last 20 lines with timestamps
tail -20 oc-memory.log | cat -n
```

### Real-time Log Monitoring

```bash
# Watch logs as they're written
tail -f oc-memory.log

# Exit with Ctrl+C
```

### Find Specific Events

```bash
# Find file sync events
grep "Synced to memory" oc-memory.log

# Find errors
grep "ERROR" oc-memory.log

# Find a specific file
grep "test_note.md" oc-memory.log

# See the last 5 sync operations
grep "Synced to memory" oc-memory.log | tail -5
```

### Enable Debug Logging

For detailed troubleshooting, enable DEBUG logging:

```yaml
# In config.yaml
logging:
  level: DEBUG
  file: oc-memory.log
```

Then restart the observer. Debug logs show:
- File detection details
- Directory scanning
- Configuration loading
- Metadata processing

---

## Checking Memory Directory

### List All Memory Files

```bash
# Count total files
find ~/.openclaw/workspace/memory -name "*.md" -type f | wc -l

# List all files with categories
find ~/.openclaw/workspace/memory -name "*.md" -type f | sort

# List just filenames
ls -R ~/.openclaw/workspace/memory
```

### Check Specific Categories

```bash
# Notes
ls ~/.openclaw/workspace/memory/notes/

# Projects
ls ~/.openclaw/workspace/memory/projects/

# Documents
ls ~/.openclaw/workspace/memory/documents/

# General (uncategorized)
ls ~/.openclaw/workspace/memory/general/
```

### View File Metadata

```bash
# View the frontmatter (first 10 lines)
head -20 ~/.openclaw/workspace/memory/notes/test_note.md

# View full file content
cat ~/.openclaw/workspace/memory/notes/test_note.md
```

### Verify Files in OpenClaw

```bash
# Check if OpenClaw database exists
ls -la ~/.openclaw/agents/main/memory.db

# Verify memory directory is readable by OpenClaw
ls -la ~/.openclaw/workspace/memory/
```

---

## Advanced Usage

### Monitoring Multiple Directories

Edit `config.yaml` to watch multiple locations:

```yaml
watch:
  dirs:
    - ~/Documents/notes
    - ~/Projects
    - ~/Desktop/inbox
    - ~/work/documentation
    - ~/research-notes
  recursive: true
```

### Custom Categorization

Currently, categories are auto-detected from file paths. To use specific categories:

Manually organize your source files:
```
~/Documents/notes/         → notes/
~/Projects/                → projects/
~/Documents/meeting-notes/ → documents/
~/research/               → general/
```

### Running Multiple Instances

You can run multiple observers for different directory sets:

**Observer 1** - Personal notes:
```bash
python memory_observer.py --config config-personal.yaml
```

**Observer 2** - Work files:
```bash
python memory_observer.py --config config-work.yaml
```

Each with their own `config.yaml` file.

### Disable Console Output

For background operation, disable console logging:

```yaml
logging:
  level: INFO
  file: oc-memory.log
  console: false
```

### Increase Log Retention

Monitor the log file size and archive old logs:

```bash
# Check current log size
du -h oc-memory.log

# Archive and compress
mv oc-memory.log oc-memory-2026-02-12.log.gz
gzip oc-memory-2026-02-12.log
```

---

## Common Issues and Troubleshooting

### Files Not Detected

**Problem:** You create/modify `.md` files but nothing appears in logs.

**Solutions:**

1. **Check watch directories exist:**
   ```bash
   ls -la ~/Documents/notes
   ls -la ~/Projects
   ```
   Create them if missing:
   ```bash
   mkdir -p ~/Documents/notes
   mkdir -p ~/Projects
   ```

2. **Verify file extension:**
   - Files must be `.md` or `.markdown`
   - Check: `ls -la ~/Documents/notes/*.md`

3. **Enable debug logging:**
   ```yaml
   # In config.yaml
   logging:
     level: DEBUG
   ```
   Restart observer and check logs:
   ```bash
   tail -f oc-memory.log | grep "detecting\|watching"
   ```

4. **Check file write completed:**
   - Some editors save asynchronously
   - Wait 2-3 seconds after saving
   - Some cloud sync tools can interfere with file watching

5. **Verify config file:**
   ```bash
   python << 'EOF'
   from lib.config import get_config
   config = get_config('config.yaml')
   print("Watch dirs:", config['watch']['dirs'])
   EOF
   ```

**Common cause:** Typo in directory paths (e.g., `~/Document` instead of `~/Documents`)

### Files Not Appearing in Memory Directory

**Problem:** Files are detected but don't appear in `~/.openclaw/workspace/memory/`

**Solutions:**

1. **Check memory directory permissions:**
   ```bash
   ls -la ~/.openclaw/workspace/
   chmod -R 755 ~/.openclaw/workspace/memory
   ```

2. **Verify memory directory in config:**
   ```bash
   python lib/config.py
   # Should show: memory_dir: ~/.openclaw/workspace/memory
   ```

3. **Check for copy errors in logs:**
   ```bash
   grep "Error\|Failed" oc-memory.log
   ```

4. **Verify source file is readable:**
   ```bash
   cat ~/Documents/notes/test.md  # Should display content
   ```

5. **Check disk space:**
   ```bash
   df -h ~/
   # Make sure you have at least 10% free space
   ```

**Common cause:** Memory directory doesn't exist or wrong path configured

### OpenClaw Not Finding Memories

**Problem:** Files are synced to memory directory, but OpenClaw can't find them.

**Solutions:**

1. **Wait for indexing (5-10 seconds):**
   - OpenClaw indexes files automatically after syncing
   - New files may take up to 10 seconds to become searchable

2. **Check OpenClaw memory database:**
   ```bash
   ls -la ~/.openclaw/agents/main/memory.db
   ```

3. **Verify file format:**
   - Files must be valid Markdown
   - Check for syntax errors:
   ```bash
   head -5 ~/.openclaw/workspace/memory/notes/test.md
   ```

4. **Restart OpenClaw:**
   - Stop and restart your OpenClaw session
   - This forces re-indexing of memory files

5. **Check OpenClaw memory configuration:**
   - In OpenClaw, verify memory directory path:
   ```bash
   grep -r "memory" ~/.openclaw/config.yaml
   ```

**Common cause:** Timing issue - wait 10 seconds and try again

### Setup Fails with Config Error

**Problem:** `ConfigError: Configuration error` when starting observer

**Solutions:**

1. **Check config file exists:**
   ```bash
   ls -la config.yaml
   ```

2. **If missing, create from template:**
   ```bash
   cp config.example.yaml config.yaml
   # Edit as needed
   ```

3. **Validate YAML syntax:**
   ```bash
   python << 'EOF'
   import yaml
   with open('config.yaml') as f:
       config = yaml.safe_load(f)
   print("Config loaded successfully")
   print(f"Watch dirs: {config['watch']['dirs']}")
   EOF
   ```

4. **Check for typos in config.yaml:**
   - Ensure proper indentation (2 spaces)
   - Check directory paths use `~` or absolute paths
   - Quote paths with spaces: `"~/My Documents"`

5. **Expand home directory:**
   Ensure paths in config use `~` which gets expanded:
   ```yaml
   # Good
   watch:
     dirs:
       - ~/Documents/notes

   # Also good
   watch:
     dirs:
       - /Users/username/Documents/notes
   ```

**Common cause:** Invalid YAML indentation or missing required fields

### Observer Crashes or Stops

**Problem:** Observer starts but exits after a few seconds.

**Solutions:**

1. **Check for errors in logs:**
   ```bash
   tail -50 oc-memory.log
   grep "Exception\|Error\|Traceback" oc-memory.log
   ```

2. **Verify watch directories are readable:**
   ```bash
   test -r ~/Documents/notes && echo "readable" || echo "not readable"
   ```

3. **Check for permission issues:**
   ```bash
   chmod +rx ~/Documents/notes
   chmod +rx ~/.openclaw/workspace/memory
   ```

4. **Run with verbose output:**
   ```bash
   # Temporarily set to DEBUG
   sed -i 's/level: INFO/level: DEBUG/' config.yaml
   python memory_observer.py
   ```

5. **Check Python environment:**
   ```bash
   which python
   python -c "import lib.file_watcher; print('OK')"
   ```

**Common cause:** Missing directory or permission denied error

### High CPU Usage

**Problem:** Observer uses a lot of CPU/disk I/O.

**Solutions:**

1. **Reduce watch scope:**
   - Monitor fewer directories in `config.yaml`
   - Exclude cloud-synced folders (Dropbox, Google Drive, iCloud)

2. **Disable recursive watching:**
   ```yaml
   watch:
     recursive: false  # Only watch root directory
   ```

3. **Set appropriate log level:**
   ```yaml
   logging:
     level: INFO    # Not DEBUG
   ```

4. **Exclude large directories:**
   - Don't watch: node_modules, .git, __pycache__, .venv
   - Keep watch paths to small, focused directories

**Common cause:** Watching node_modules or other large directories with many files

---

## Production Deployment

For running OC-Memory in production (continuously, even after restart), see [DEPLOYMENT.md](DEPLOYMENT.md) for:

- **systemd setup** (Linux) - Auto-restart service
- **LaunchAgent setup** (macOS) - Run at login
- **Task Scheduler** (Windows) - Auto-restart service
- **Docker deployment** - Containerized setup
- **Monitoring and alerts** - Health checks

---

## Testing Components Individually

### Test FileWatcher Component

```bash
python << 'EOF'
from lib.file_watcher import FileWatcher
import time

print("Testing FileWatcher component...")
print("Create/edit .md files in ~/Documents/notes to test")
print("Press Ctrl+C to stop\n")

def callback(path, event_type):
    print(f"✅ {event_type}: {path}")

watcher = FileWatcher(['~/Documents/notes'], callback=callback)
watcher.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopping...")
    watcher.stop()
EOF
```

### Test MemoryWriter Component

```bash
python << 'EOF'
from lib.memory_writer import MemoryWriter
from pathlib import Path
from datetime import datetime

print("Testing MemoryWriter component...")

writer = MemoryWriter('~/.openclaw/workspace/memory')

# Test: Create memory entry
print("\n1. Creating memory entry...")
content = "# Test Entry\nThis is a test."
result = writer.write_memory_entry(
    content=content,
    filename="test_entry.md",
    category="tests"
)
print(f"✅ Created: {result}")

# Test: Add metadata
print("\n2. Adding metadata...")
writer.add_metadata(result, {
    "created": datetime.now().isoformat(),
    "category": "test",
    "tags": ["test"]
})
print(f"✅ Metadata added")

# Test: Category detection
print("\n3. Testing category detection...")
test_paths = [
    Path("~/Documents/notes/note.md"),
    Path("~/Projects/proj.md"),
    Path("~/Documents/doc.md"),
]
for p in test_paths:
    cat = writer.get_category_from_path(p)
    print(f"   {p.name:20} → {cat}")

print("\n✅ All tests passed!")
EOF
```

### Test Configuration Loading

```bash
python << 'EOF'
from lib.config import get_config

print("Testing configuration loading...")
config = get_config('config.yaml')

print(f"\nConfiguration loaded:")
print(f"  Watch directories: {config['watch']['dirs']}")
print(f"  Recursive: {config['watch'].get('recursive', True)}")
print(f"  Memory directory: {config['memory']['dir']}")
print(f"  Auto-categorize: {config['memory'].get('auto_categorize', True)}")
print(f"  Log level: {config.get('logging', {}).get('level', 'INFO')}")

print("\n✅ Configuration is valid!")
EOF
```

---

## Summary

### 5-Minute Quick Start

```bash
# 1. Clone and setup
git clone https://github.com/openclaw-ai/oc-memory.git
cd oc-memory
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure (optional - defaults work)
nano config.yaml

# 3. Start observer
python memory_observer.py

# 4. In another terminal, create a test file
mkdir -p ~/Documents/notes
echo "# Test" > ~/Documents/notes/test.md

# 5. Check memory directory
ls ~/.openclaw/workspace/memory/notes/
```

### Success Indicators

You'll know it's working when:

1. ✅ Observer starts without errors
2. ✅ Creating/editing `.md` files appears in logs within 2 seconds
3. ✅ Files appear in `~/.openclaw/workspace/memory/[category]/`
4. ✅ Files have YAML frontmatter with metadata
5. ✅ OpenClaw can find your memories (after 5-10 second indexing)

### Next Steps

1. ✅ **Getting Started** - You're here!
2. ➡️ **Run Tests** - Use `pytest` to verify components: `pytest tests/`
3. ➡️ **Production Setup** - See [DEPLOYMENT.md](DEPLOYMENT.md) for continuous operation
4. ➡️ **API Docs** - See [API.md](API.md) for advanced integration
5. ➡️ **Architecture** - See [CLAUDE.md](../CLAUDE.md) for system design

---

## Additional Resources

- **[README.md](../README.md)** - Project overview and features
- **[CLAUDE.md](../CLAUDE.md)** - Developer guide and architecture
- **[TESTING.md](TESTING.md)** - Comprehensive testing guide
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide
- **[API.md](API.md)** - API documentation and integration examples
- **[OpenClaw Repository](https://github.com/openclaw-ai/openclaw)** - Official OpenClaw repo

---

## Tips for Best Results

1. **Start simple:** Monitor one directory initially (e.g., `~/Documents/notes`)
2. **Use consistent naming:** File paths are used for categorization
3. **Check logs regularly:** Watch `oc-memory.log` to understand behavior
4. **Avoid cloud directories:** Don't monitor Dropbox/Google Drive/iCloud - they interfere with file watching
5. **Keep watch scope small:** Monitor only directories with actual content
6. **Use meaningful file names:** Better for searchability and categorization
7. **Add frontmatter manually:** Optional, but helps with OpenClaw's memory search

---

## Getting Help

If you encounter issues:

1. Check [Common Issues](#common-issues-and-troubleshooting) above
2. Enable DEBUG logging and review logs
3. Verify configuration with `python lib/config.py`
4. Test individual components (see [Testing Components](#testing-components-individually))
5. Check [TESTING.md](TESTING.md) for comprehensive testing procedures
6. Review [CLAUDE.md](../CLAUDE.md) for architectural details

---

**Version:** 1.1
**Status:** Ready for production use
**Last Updated:** 2026-02-12
