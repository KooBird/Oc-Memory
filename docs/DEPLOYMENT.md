# Deployment Guide

Production deployment guide for OC-Memory with performance optimization, monitoring, and CI/CD.

## Pre-Deployment Checklist

- [x] All unit tests passing (66+ tests)
- [x] Integration tests passing
- [x] Code coverage 75%+
- [x] Performance benchmarks validated
- [x] Error handling implemented
- [x] Logging configured
- [x] Monitoring setup
- [x] CI/CD pipeline configured

## 1. Performance Optimization

### 1.1 Performance Targets

OC-Memory must achieve:
- **Processing Speed:** 1000+ files/second
- **Memory Usage:** <100MB for 100 files
- **Latency:** <1ms per file
- **Reliability:** 99.9% uptime

### 1.2 Performance Configuration

Edit `config.yaml` for production:

```yaml
watch:
  dirs:
    - ~/.openclaw/workspace/memory
    - ~/Documents/notes
  recursive: true
  poll_interval: 1.0

memory:
  dir: ~/.openclaw/workspace/memory
  auto_categorize: true
  max_file_size: 10485760  # 10MB

logging:
  level: INFO              # Production: INFO (not DEBUG)
  file: ~/.openclaw/logs/oc-memory.log
  console: false           # Background operation

hot_memory:
  ttl_days: 90
  max_observations: 50000

llm:
  enabled: false          # Enable only if needed
```

### 1.3 Performance Testing

```bash
# Test with 100 files
for i in {1..100}; do
  echo "# Test $i" > ~/Documents/notes/test_$i.md
done

# Measure processing time
time python memory_observer.py

# Expected: <0.1 seconds for 100 files (1000+ files/sec)
```

### 1.4 Memory Monitoring

```python
# Monitor memory usage during extended operation
import psutil
import time

process = psutil.Process()
for i in range(60):
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"Memory: {memory_mb:.2f} MB")
    time.sleep(60)
```

## 2. Environment Configuration

### 2.1 Production Environment Variables

Create `config/.env.production`:

```bash
# Logging
OC_MEMORY_LOG_LEVEL=INFO
OC_MEMORY_LOG_FILE=~/.openclaw/logs/oc-memory.log
OC_MEMORY_CONSOLE_OUTPUT=false

# Configuration
OC_MEMORY_CONFIG_PATH=~/.openclaw/config.yaml
OC_MEMORY_DATA_DIR=~/.openclaw/workspace/memory

# Performance
OC_MEMORY_MAX_WORKERS=4
OC_MEMORY_BATCH_SIZE=100
OC_MEMORY_CACHE_SIZE=1000

# Monitoring
OC_MEMORY_HEALTH_CHECK_INTERVAL=3600  # 1 hour
OC_MEMORY_METRICS_ENABLED=true

# Error Handling
OC_MEMORY_RETRY_ATTEMPTS=3
OC_MEMORY_RETRY_DELAY=2

# Features
OC_MEMORY_AUTO_CATEGORIZE=true
OC_MEMORY_PRESERVE_METADATA=true
```

Load environment variables:

```bash
# In deployment scripts
set -a
source config/.env.production
set +a

# Or in systemd service
EnvironmentFile=/path/to/config/.env.production
```

### 2.2 Directory Setup

```bash
# Create necessary directories
mkdir -p ~/.openclaw/logs
mkdir -p ~/.openclaw/workspace/memory
mkdir -p ~/.openclaw/config

# Set appropriate permissions
chmod 755 ~/.openclaw
chmod 755 ~/.openclaw/logs
chmod 755 ~/.openclaw/workspace/memory
```

## 3. Error Handling and Recovery

### 3.1 Exception Handling

The system handles:
- **PermissionError**: Files with read-only permissions
- **FileNotFoundError**: Deleted files during processing
- **OSError**: Disk space issues
- **MemoryError**: Resource exhaustion

### 3.2 Retry Logic with Exponential Backoff

```python
# Configured in lib/file_watcher.py
retry_attempts: 3
retry_delay: 2  # Exponential: 2s, 4s, 8s

# Handles transient failures automatically
```

### 3.3 Graceful Shutdown

```bash
# Send SIGTERM to daemon
kill -TERM <PID>

# System will:
# 1. Stop accepting new files
# 2. Complete current processing
# 3. Log final statistics
# 4. Exit cleanly
```

## 4. Monitoring and Health Checks

### 4.1 Performance Metrics

OC-Memory collects:
- `total_files_processed`: Files successfully processed
- `total_errors`: Processing errors
- `avg_processing_time_ms`: Average latency
- `peak_memory_mb`: Maximum memory used
- `uptime_seconds`: System uptime
- `success_rate`: Percentage of successful operations

View metrics in logs:

```bash
grep "Performance Metrics" ~/.openclaw/logs/oc-memory.log
```

### 4.2 Health Checks

Automatic health checks verify:
- Memory directory exists and is writable
- Disk space available (minimum 1GB)
- Memory usage within limits (max 80%)
- Log file size reasonable (max 100MB)

Configure check interval:

```yaml
# config.yaml
monitoring:
  health_check_interval: 3600  # 1 hour
```

### 4.3 Log Monitoring

```bash
# Real-time monitoring
tail -f ~/.openclaw/logs/oc-memory.log

# Search for errors
grep ERROR ~/.openclaw/logs/oc-memory.log

# Extract metrics
grep "Performance Metrics" ~/.openclaw/logs/oc-memory.log | tail -1

# Monitor system health
grep "Health check" ~/.openclaw/logs/oc-memory.log
```

## 5. CI/CD Pipeline

### 5.1 GitHub Actions Configuration

File: `.github/workflows/tests.yml`

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
        python-version: ['3.10', '3.11', '3.12']

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Lint with flake8
      run: |
        pip install flake8
        flake8 lib/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 lib/ tests/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

    - name: Run tests
      run: |
        pytest tests/ -v --cov=lib --cov-report=xml

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage.xml
        flags: unittests
        name: codecov-umbrella

    - name: Check coverage threshold
      run: |
        coverage report --fail-under=75

    - name: Archive test results
      if: always()
      uses: actions/upload-artifact@v3
      with:
        name: test-results-${{ matrix.os }}-py${{ matrix.python-version }}
        path: coverage.xml
```

### 5.2 Coverage Requirements

- **Minimum Coverage:** 75%
- **Target Coverage:** 85%+
- **Critical Modules:** 90%+

Enforce in CI/CD:

```bash
# Fails if coverage < 75%
coverage report --fail-under=75
```

### 5.3 Code Quality Checks

```bash
# Lint checks
flake8 lib/ tests/ --max-complexity=10 --max-line-length=127

# Type checking
mypy lib/

# Security checks
bandit -r lib/
```

## 6. Deployment Process

### 6.1 Pre-Deployment Steps

```bash
# 1. Verify all tests pass
pytest tests/ -v

# 2. Check coverage
pytest tests/ --cov=lib --cov-fail-under=75

# 3. Lint code
flake8 lib/ tests/

# 4. Run performance tests
python -m pytest tests/test_performance.py -v
```

### 6.2 Deployment to Production

```bash
# 1. Create release tag
git tag -a v1.0.0 -m "Production release"
git push origin v1.0.0

# 2. GitHub Actions automatically:
#    - Runs all tests
#    - Generates release
#    - Publishes artifacts

# 3. Deploy to target system
./deploy.sh production

# 4. Verify deployment
./health_check.sh
```

### 6.3 Rollback Procedure

```bash
# If deployment fails:

# 1. Stop current version
sudo systemctl stop oc-memory

# 2. Revert to previous release
git checkout v0.9.0

# 3. Reinstall dependencies
pip install -r requirements.txt

# 4. Restart service
sudo systemctl start oc-memory

# 5. Verify health
./health_check.sh
```

## 7. Running as a Service

### 7.1 Linux (systemd)

Create `/etc/systemd/system/oc-memory.service`:

```ini
[Unit]
Description=OC-Memory Observer
After=network.target

[Service]
Type=simple
User=openclaw
WorkingDirectory=/opt/oc-memory
ExecStart=/usr/bin/python3 memory_observer.py
Restart=always
RestartSec=10
EnvironmentFile=/opt/oc-memory/config/.env.production

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable oc-memory
sudo systemctl start oc-memory
sudo systemctl status oc-memory
```

### 7.2 macOS (LaunchAgent)

Create `~/Library/LaunchAgents/com.oc-memory.observer.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.oc-memory.observer</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/opt/oc-memory/memory_observer.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/opt/oc-memory</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>/var/log/oc-memory.err</string>
    <key>StandardOutPath</key>
    <string>/var/log/oc-memory.log</string>
</dict>
</plist>
```

Load and verify:

```bash
launchctl load ~/Library/LaunchAgents/com.oc-memory.observer.plist
launchctl list | grep oc-memory
```

### 7.3 Windows (Task Scheduler)

Use NSSM (Non-Sucking Service Manager):

```bash
# Install
nssm install oc-memory "C:\Python311\python.exe" "C:\oc-memory\memory_observer.py"

# Configure
nssm set oc-memory AppDirectory "C:\oc-memory"
nssm set oc-memory AppStdout "C:\oc-memory\logs\oc-memory.log"
nssm set oc-memory AppStderr "C:\oc-memory\logs\oc-memory.err"

# Start
nssm start oc-memory
```

## 8. Monitoring and Alerting

### 8.1 Key Metrics to Monitor

```
- Files processed per hour
- Error rate (target: <1%)
- Average processing time
- Memory usage trend
- Uptime percentage
```

### 8.2 Alert Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| Error Rate | >0.5% | >2% |
| Memory Usage | >70% | >90% |
| Disk Space | <10% | <5% |
| Uptime | <99.5% | <99% |
| Processing Time | >10ms | >50ms |

### 8.3 Log Analysis

```bash
# Count errors per hour
grep ERROR ~/.openclaw/logs/oc-memory.log | \
  cut -d' ' -f1-2 | sort | uniq -c

# Find performance issues
grep "Performance Metrics" ~/.openclaw/logs/oc-memory.log | \
  grep -v "success_rate.*100"

# Monitor memory growth
grep "Process Stats" ~/.openclaw/logs/oc-memory.log | \
  tail -10
```

## 9. Troubleshooting

### 9.1 High Memory Usage

```bash
# 1. Check for leaks
python -m memory_profiler memory_observer.py

# 2. Monitor growth
watch -n 1 'ps aux | grep memory_observer'

# 3. Restart if necessary
sudo systemctl restart oc-memory
```

### 9.2 Processing Delays

```bash
# 1. Check log backlog
tail -f ~/.openclaw/logs/oc-memory.log | grep "Processing file"

# 2. Monitor disk I/O
iostat -x 1

# 3. Check file permissions
ls -la ~/Documents/notes/
```

### 9.3 Integration Issues

```bash
# 1. Verify OpenClaw memory directory
ls -la ~/.openclaw/workspace/memory/

# 2. Check file format
head -5 ~/.openclaw/workspace/memory/notes/*.md

# 3. Test memory search
openclaw memory search "test"
```

## 10. Production Checklist

Before going live, verify:

- [x] Performance tests passing (1000+ files/sec)
- [x] Error handling working for all scenarios
- [x] Monitoring and alerting configured
- [x] Health checks running (every 1 hour)
- [x] Logs rotating properly
- [x] Systemd service configured
- [x] Rollback procedure documented
- [x] Backup strategy in place
- [x] Security review completed
- [x] Documentation updated

## Support and Resources

- **Issue Tracker:** https://github.com/openclaw-ai/oc-memory/issues
- **Documentation:** See [TESTING.md](TESTING.md) for test procedures
- **Configuration:** See [README.md](../README.md) for full reference
- **Architecture:** See [architecture/](architecture/) for system design

---

**Version:** 1.0
**Status:** Production-ready
**Last Updated:** 2026-02-12
