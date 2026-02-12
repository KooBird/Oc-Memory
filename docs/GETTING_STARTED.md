# Getting Started with OC-Memory

Get up and running with OC-Memory in under 5 minutes!

## Prerequisites

Ensure you have the following installed:
- Python 3.10+
- pip
- Virtual environment (recommended)

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/openclaw-ai/oc-memory.git
cd oc-memory

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

## Configuration

### Basic Setup (5 minutes)

The default config file `config.yaml` is pre-configured:

```yaml
watch:
  dirs:
    - ~/Documents/notes
    - ~/Projects

memory:
  dir: ~/.openclaw/workspace/memory
```

**Customize if needed:**
```bash
# Edit configuration
nano config.yaml  # or your preferred editor
```

### Key Configuration Options

#### Watch Directories

Add or modify directories to monitor for markdown files:

```yaml
watch:
  dirs:
    - ~/Documents/notes
    - ~/Projects
    - ~/Desktop/scratch
```

#### Memory Directory

**Important:** Match this to OpenClaw's memory path:

```yaml
memory:
  dir: ~/.openclaw/workspace/memory
```

#### Logging

```yaml
logging:
  level: INFO  # DEBUG for verbose output, INFO for production
  file: oc-memory.log
  console: true  # Set to false for background operation
```

## Running OC-Memory

### Starting the Observer

```bash
# Activate virtual environment (if not already activated)
source venv/bin/activate

# Start the memory observer daemon
python memory_observer.py
```

You should see output like:

```
========================================
Starting OC-Memory Observer
========================================
Watch directories: ['/Users/your-username/Documents/notes', ...]
Memory directory: /Users/your-username/.openclaw/workspace/memory
========================================
OC-Memory Observer started successfully
Monitoring for file changes... (Press Ctrl+C to stop)
```

### Testing the System

**Terminal 1: Start the observer**
```bash
source venv/bin/activate
python memory_observer.py
```

**Terminal 2: Create a test note**
```bash
# Create test directory
mkdir -p ~/Documents/notes

# Create test note
echo "# My First Memory" > ~/Documents/notes/test_note.md
echo "" >> ~/Documents/notes/test_note.md
echo "This is a test memory entry for OC-Memory." >> ~/Documents/notes/test_note.md
```

**Expected behavior:**
1. FileWatcher detects the new file
2. MemoryWriter copies it to `~/.openclaw/workspace/memory/notes/`
3. Metadata is added (timestamp, category, source path)
4. OpenClaw auto-indexes it within ~5 seconds

### Verifying in OpenClaw

**Check the memory directory:**
```bash
ls ~/.openclaw/workspace/memory/notes/
```

**In OpenClaw CLI:**
```
Use memory_search tool to find "test memory"
```

## Testing Components Individually

### Test FileWatcher
```bash
python lib/file_watcher.py
# In another terminal: create/edit .md files in ~/Documents/notes
```

### Test MemoryWriter
```bash
python lib/memory_writer.py
# Runs built-in tests automatically
```

### Test Config
```bash
python lib/config.py
# Shows loaded configuration
```

## Directory Structure

Once running, OC-Memory creates the following memory structure:

```
~/.openclaw/workspace/memory/
├── notes/           # Auto-categorized notes
│   └── test_note.md
├── projects/        # Project-related files
├── documents/       # General documents
└── general/         # Uncategorized files
```

## Advanced Testing (Phase 2)

For comprehensive testing of file watching and memory synchronization:

### Phase 2 Test 1: FileWatcher Real-time Detection (5 minutes)

**Terminal 1: Start FileWatcher**
```bash
source venv/bin/activate
python << 'PYTHON'
from lib.file_watcher import FileWatcher
import time

events = []
def callback(file_path, event_type):
    events.append((str(file_path.name), event_type))
    print(f"✅ {event_type}: {file_path.name}")

watcher = FileWatcher(
    watch_dirs=['~/Documents/notes'],
    callback=callback
)

print("🚀 FileWatcher started. Waiting for changes...")
watcher.start()

try:
    for i in range(10):
        print(f"  {i+1}...", end=' ', flush=True)
        time.sleep(1)
    print()
except KeyboardInterrupt:
    pass

watcher.stop()
print(f"\n📊 Captured {len(events)} events:")
for filename, event_type in events:
    print(f"  {event_type}: {filename}")
PYTHON
```

**Terminal 2: Create/modify files (while watcher is running)**
```bash
# Wait 3 seconds then create files
sleep 3
touch ~/Documents/notes/new_file.md
echo "# Updated" >> ~/Documents/notes/test.md
echo "# Another file" > ~/Documents/notes/another.md
```

**Success criteria:** 3+ file events detected

### Phase 2 Test 2: MemoryWriter File Copying (3 minutes)

```bash
source venv/bin/activate

python << 'PYTHON'
from lib.config import get_config
from lib.memory_writer import MemoryWriter
from pathlib import Path

# Load configuration
config = get_config('config.yaml')

# Initialize MemoryWriter
writer = MemoryWriter(config['memory']['dir'])

# Prepare test file
test_file = Path('~/Documents/notes/test.md').expanduser()

print(f"📄 Source: {test_file}")
print(f"  Exists: {test_file.exists()}")

# Copy file
category = writer.get_category_from_path(test_file)
print(f"🏷️  Category: {category}")

target = writer.copy_to_memory(test_file, category=category)
print(f"✅ Copied to: {target}")

# Add metadata
from datetime import datetime
writer.add_metadata(target, {
    'source': str(test_file),
    'copied_at': datetime.now().isoformat()
})
print(f"✅ Metadata added")

# Verify
assert target.exists(), "Target not found!"
print(f"✅ Verification passed!")

# Check memory directory
memory_dir = Path(config['memory']['dir'])
files = list(memory_dir.rglob('*.md'))
print(f"\n📁 Memory directory files: {len(files)}")
for f in files[:5]:
    print(f"  {f.relative_to(memory_dir)}")
PYTHON
```

**Success criteria:** File copied with metadata added successfully

### Phase 2 Test 3: Memory Observer Daemon (5 minutes)

**Terminal 1: Start observer daemon**
```bash
source venv/bin/activate
python memory_observer.py
```

**Terminal 2: Create test file (while daemon is running)**
```bash
sleep 2
echo "# Integration test" > ~/Documents/notes/integration_test.md
echo "✅ File created"
sleep 2
```

**Expected output in Terminal 1:**
```
2026-02-12 10:30:47,200 - lib.file_watcher - INFO - New markdown file detected: .../integration_test.md
2026-02-12 10:30:47,201 - memory_observer - INFO - Processing file: .../integration_test.md (created)
2026-02-12 10:30:47,202 - memory_observer - INFO - Synced to memory: .../notes/integration_test.md (total: 1)
```

**Stop with Ctrl+C:**
```
Received keyboard interrupt
Stopping OC-Memory Observer...
============================================================
OC-Memory Observer Statistics
============================================================
Files processed: 1
Errors: 0
============================================================
OC-Memory Observer stopped
```

**Success criteria:** Daemon starts/processes files/stops cleanly

## Monitoring Logs

```bash
# View log file
tail -100 oc-memory.log

# Real-time log monitoring
tail -f oc-memory.log

# Check memory directory contents
find ~/.openclaw/workspace/memory -type f -name "*.md" | wc -l
```

## Troubleshooting

### Files Not Being Detected

1. **Check watch directories exist:**
   ```bash
   ls ~/Documents/notes
   ```

2. **Enable debug logging:**
   Edit `config.yaml`:
   ```yaml
   logging:
     level: DEBUG
   ```

3. **Check logs:**
   ```bash
   tail -f oc-memory.log
   ```

### Memory Files Not Created

1. **Check memory directory permissions:**
   ```bash
   ls -la ~/.openclaw/workspace/
   ```

2. **Verify config path:**
   ```bash
   python lib/config.py
   ```

### OpenClaw Not Finding Memories

1. **Wait 5-10 seconds** for auto-indexing

2. **Check OpenClaw memory database:**
   ```bash
   ls ~/.openclaw/agents/main/memory.db
   ```

3. **Verify file format** (must be valid Markdown)

## Production Setup

### Running as Background Service (Linux/macOS)

**systemd (Linux):**
```bash
# Create service file
sudo nano /etc/systemd/system/oc-memory.service

# Add content:
[Unit]
Description=OC-Memory Observer
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/oc-memory
ExecStart=/usr/bin/python3 memory_observer.py
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable oc-memory
sudo systemctl start oc-memory
sudo systemctl status oc-memory
```

**LaunchAgent (macOS):**
```bash
# Create plist file
nano ~/Library/LaunchAgents/com.oc-memory.observer.plist

# Add content:
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.oc-memory.observer</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/oc-memory/memory_observer.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/path/to/oc-memory</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>

# Load
launchctl load ~/Library/LaunchAgents/com.oc-memory.observer.plist
```

### Windows Service

Use NSSM (Non-Sucking Service Manager) or Task Scheduler.

## Next Steps

1. ✅ **Getting Started**: Complete the 5-minute setup above
2. ➡️ **Run Tests**: Use pytest to verify functionality
3. ➡️ **Production Deployment**: See [DEPLOYMENT.md](DEPLOYMENT.md)
4. ➡️ **API Documentation**: See [API.md](API.md)

## Documentation

- **[README.md](../README.md)** - Project overview
- **[CLAUDE.md](../CLAUDE.md)** - Developer guide
- **[TESTING.md](TESTING.md)** - Testing guide
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deployment guide

## Tips

1. **Use consistent naming** in your notes for better categorization
2. **Add frontmatter** to your markdown files for better metadata
3. **Monitor the logs** during initial testing to understand behavior
4. **Start with one directory** and expand after confirming it works

## Success Criteria

You'll know it's working when:

1. ✅ Observer starts without errors
2. ✅ Creating/editing .md files triggers log messages
3. ✅ Files appear in `~/.openclaw/workspace/memory/`
4. ✅ OpenClaw's memory_search finds your content
5. ✅ Metadata is automatically added to files

---

**Version:** 1.0
**Status:** Ready for production use
**Last Updated:** 2026-02-12
