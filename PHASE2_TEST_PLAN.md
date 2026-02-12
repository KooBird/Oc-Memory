# 🧪 OC-Memory Phase 2 테스트 계획

**계획 날짜**: 2026-02-12
**목표**: memory_observer.py 통합 테스트 및 실제 동작 검증

---

## 📋 Phase 2 테스트 우선순위

### 🔴 Priority 1 (필수) - 실제 작동 검증

#### 1-1: FileWatcher 실제 작동 테스트
**목표**: FileWatcher가 실제 파일 변경을 감지하는지 검증

**테스트 절차**:
```bash
# Step 1: 감시 디렉토리 준비
mkdir -p ~/Documents/notes
mkdir -p ~/Projects

# Step 2: 테스트 파일 생성
cat > ~/Documents/notes/test1.md << 'EOF'
# Test Note 1
Created for FileWatcher testing
EOF

# Step 3: Python에서 FileWatcher 직접 테스트
source venv/bin/activate
python << 'PYTHON'
from lib.file_watcher import FileWatcher
from pathlib import Path
import time

# 콜백 함수 정의
events = []
def test_callback(file_path, event_type):
    events.append({
        'file': str(file_path),
        'event': event_type,
        'timestamp': time.time()
    })
    print(f"✅ Event: {event_type} - {file_path.name}")

# FileWatcher 시작
watcher = FileWatcher(
    watch_dirs=['~/Documents/notes'],
    callback=test_callback,
    recursive=True
)

print("🚀 Starting FileWatcher...")
watcher.start()

# 파일 변경 대기
print("⏳ Waiting for file events (10 seconds)...")
time.sleep(2)

# 다른 프로세스에서 파일 수정하기 (외부에서)
print("📝 Ready for external file changes...")

try:
    for i in range(8):
        time.sleep(1)
        print(f"  {i+1}... ", end='', flush=True)
    print()
except KeyboardInterrupt:
    pass

# 결과 출력
watcher.stop()
print(f"\n📊 Results:")
print(f"  Events captured: {len(events)}")
for event in events:
    print(f"    - {event['event']}: {Path(event['file']).name}")
PYTHON

# Step 4: 다른 터미널에서 파일 수정 (위 스크립트 실행 중)
# 새로운 터미널 열고 아래 실행:
echo "# Updated content" >> ~/Documents/notes/test1.md
touch ~/Documents/notes/test2.md
```

**검증 포인트**:
- [ ] FileWatcher가 정상 시작
- [ ] 파일 생성 이벤트 감지
- [ ] 파일 수정 이벤트 감지
- [ ] 콜백 함수 호출 확인
- [ ] 경로 정보 정확성

**성공 기준**: 2개 이상의 이벤트 감지

---

#### 1-2: MemoryWriter 파일 복사 테스트
**목표**: MemoryWriter가 파일을 올바르게 메모리 디렉토리에 복사하는지 검증

**테스트 절차**:
```bash
source venv/bin/activate

python << 'PYTHON'
from lib.config import get_config
from lib.memory_writer import MemoryWriter
from pathlib import Path
import os

# 설정 로드
config = get_config('config.yaml')

# MemoryWriter 초기화
memory_dir = config['memory']['dir']
writer = MemoryWriter(memory_dir)

print(f"📁 Memory directory: {memory_dir}")
print(f"✅ MemoryWriter initialized")

# 테스트 파일 확인
test_file = Path('~/Documents/notes/test1.md').expanduser()
if not test_file.exists():
    print(f"⚠️  Creating test file: {test_file}")
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("# Test Content\nTest markdown file")

print(f"\n📄 Source file: {test_file}")
print(f"  Size: {test_file.stat().st_size} bytes")

# 파일 복사
try:
    # 카테고리 감지
    category = writer.get_category_from_path(test_file)
    print(f"🏷️  Detected category: {category}")

    # 파일 복사
    target = writer.copy_to_memory(test_file, category=category)
    print(f"✅ File copied: {target}")
    print(f"  Size: {target.stat().st_size} bytes")

    # 메타데이터 추가
    from datetime import datetime
    writer.add_metadata(target, {
        'source': str(test_file),
        'category': category,
        'imported_at': datetime.now().isoformat()
    })
    print(f"✅ Metadata added")

    # 복사본 검증
    assert target.exists(), "Target file not found"
    assert target.read_text() == test_file.read_text(), "Content mismatch"
    assert '---' in target.read_text(), "Metadata not found"
    print(f"\n✅ All validations passed!")

except Exception as e:
    print(f"❌ Error: {e}")
    raise
PYTHON
```

**검증 포인트**:
- [ ] 메모리 디렉토리 생성
- [ ] 파일 복사 성공
- [ ] 메타데이터 추가
- [ ] 내용 일치 확인
- [ ] 충돌 처리 (같은 파일 2번 복사)

**성공 기준**: 모든 검증 통과

---

### 🔴 Priority 2 (높음) - memory_observer.py 통합 테스트

#### 2-1: 데몬 시작/중지 테스트
**목표**: memory_observer.py가 정상적으로 시작되고 종료되는지 검증

**테스트 절차**:
```bash
source venv/bin/activate

# 터미널 1: memory_observer 시작
python memory_observer.py

# 출력 예상:
# ============================================================
# Starting OC-Memory Observer
# ============================================================
# Watch directories: ['/Users/.../Documents/notes', ...]
# Memory directory: /Users/.../workspace/memory
# ============================================================
# OC-Memory Observer started successfully
# Monitoring for file changes... (Press Ctrl+C to stop)

# (30초 후)
# 터미널에서 Ctrl+C 입력

# 예상 출력:
# Received keyboard interrupt
# Stopping OC-Memory Observer...
# ============================================================
# OC-Memory Observer Statistics
# ============================================================
# Files processed: 0
# Errors: 0
# ============================================================
# OC-Memory Observer stopped
```

**검증 포인트**:
- [ ] 프로세스 정상 시작
- [ ] 설정 파일 로드
- [ ] 감시 디렉토리 확인
- [ ] 로그 파일 생성
- [ ] Ctrl+C 정상 종료

**성공 기준**: 깔끔한 시작과 종료

---

#### 2-2: 파일 동기화 E2E 테스트
**목표**: 파일 생성 → FileWatcher 감지 → MemoryWriter 동기화 전체 흐름 검증

**테스트 절차 (3개 터미널 필요)**:

```bash
# 터미널 1: memory_observer 시작
source venv/bin/activate
python memory_observer.py
# 출력 확인 후 대기

# 터미널 2: 메모리 디렉토리 모니터링
ls -la ~/.openclaw/workspace/memory/
# 초기 파일 개수 확인 후
watch -n 1 'ls -la ~/.openclaw/workspace/memory/*/*.md | wc -l'
# (매 1초마다 파일 개수 업데이트 표시)

# 터미널 3: 테스트 파일 생성/수정
source venv/bin/activate
python << 'PYTHON'
from pathlib import Path
import time

notes_dir = Path('~/Documents/notes').expanduser()
notes_dir.mkdir(parents=True, exist_ok=True)

# 테스트 1: 새 파일 생성
test_file1 = notes_dir / 'integration_test_1.md'
test_file1.write_text('# Integration Test 1\nContent 1')
print(f"✅ Created: {test_file1.name}")

time.sleep(2)

# 테스트 2: 파일 수정
test_file1.write_text('# Integration Test 1\nContent 1 - Updated')
print(f"✅ Modified: {test_file1.name}")

time.sleep(2)

# 테스트 3: 다른 파일 생성
test_file2 = notes_dir / 'integration_test_2.md'
test_file2.write_text('# Integration Test 2\nContent 2')
print(f"✅ Created: {test_file2.name}")

time.sleep(2)

print("✅ All test files created/modified")
PYTHON
```

**모니터링 확인**:
- 터미널 1에서 로그 메시지 확인:
  ```
  [INFO] Processing file: .../integration_test_1.md (created)
  [INFO] Synced to memory: .../notes/integration_test_1.md (total: 1)
  [INFO] Processing file: .../integration_test_1.md (modified)
  [INFO] Synced to memory: .../notes/integration_test_1_YYYYMMDD_HHMMSS.md (total: 2)
  [INFO] Processing file: .../integration_test_2.md (created)
  [INFO] Synced to memory: .../notes/integration_test_2.md (total: 3)
  ```

- 터미널 2에서 파일 개수 증가 확인

**검증 포인트**:
- [ ] 파일 생성 감지 (5초 이내)
- [ ] 메모리 디렉토리 자동 생성
- [ ] 파일 복사 성공
- [ ] 메타데이터 추가
- [ ] 통계 집계 (Files processed 증가)
- [ ] 로그 파일 기록

**성공 기준**: 3개 파일 모두 메모리 디렉토리에 동기화

---

### 🟡 Priority 3 (중간) - 에러 처리 및 복구

#### 3-1: 잘못된 경로 처리
```bash
python << 'PYTHON'
from lib.file_watcher import FileWatcher
import time

# 존재하지 않는 디렉토리 감시
watcher = FileWatcher(
    watch_dirs=['/nonexistent/directory'],
    recursive=True
)

print("Starting watcher with non-existent directory...")
watcher.start()

# 로그 확인
time.sleep(1)

print(f"Is alive: {watcher.is_alive()}")
watcher.stop()
print("✅ Handled gracefully")
PYTHON
```

#### 3-2: 권한 부족 처리
```bash
mkdir -p /tmp/readonly
chmod 000 /tmp/readonly

python << 'PYTHON'
from lib.memory_writer import MemoryWriter
from pathlib import Path

try:
    writer = MemoryWriter('/tmp/readonly')
    print("❌ Should have failed due to permissions")
except PermissionError:
    print("✅ Permission error caught correctly")
except Exception as e:
    print(f"⚠️  Different error: {type(e).__name__}: {e}")
finally:
    import os
    os.chmod('/tmp/readonly', 0o755)
PYTHON
```

---

## 🧪 Phase 2 Unit Test 작성

### 새 테스트 파일: tests/test_memory_observer.py

```bash
cat > tests/test_memory_observer.py << 'PYTHON'
"""
Unit tests for memory_observer.py
Tests MemoryObserver daemon functionality
"""

import pytest
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from memory_observer import MemoryObserver


@pytest.fixture
def temp_config(temp_directory):
    """Create temporary config for testing"""
    import yaml
    config_file = temp_directory / 'test_config.yaml'

    config = {
        'watch': {
            'dirs': [str(temp_directory / 'watch')],
            'recursive': True,
            'poll_interval': 0.1
        },
        'memory': {
            'dir': str(temp_directory / 'memory'),
            'auto_categorize': True
        },
        'logging': {
            'level': 'DEBUG',
            'file': str(temp_directory / 'observer.log'),
            'console': False
        },
        'hot_memory': {'ttl_days': 90}
    }

    with open(config_file, 'w') as f:
        yaml.dump(config, f)

    # Create watch directory
    (temp_directory / 'watch').mkdir()

    return str(config_file)


class TestMemoryObserver:
    """Tests for MemoryObserver class"""

    def test_init_loads_config(self, temp_config):
        """Test that __init__ loads configuration"""
        observer = MemoryObserver(config_path=temp_config)
        assert observer.config is not None
        assert 'watch' in observer.config
        assert 'memory' in observer.config

    def test_init_with_invalid_config(self, temp_directory):
        """Test init with invalid config file"""
        invalid_config = temp_directory / 'invalid.yaml'
        invalid_config.write_text("invalid: [")

        with pytest.raises(Exception):
            MemoryObserver(config_path=str(invalid_config))

    def test_components_initialized(self, temp_config):
        """Test that FileWatcher and MemoryWriter are initialized"""
        observer = MemoryObserver(config_path=temp_config)
        assert observer.file_watcher is not None
        assert observer.memory_writer is not None

    def test_statistics_initialized(self, temp_config):
        """Test that statistics are initialized"""
        observer = MemoryObserver(config_path=temp_config)
        assert observer.files_processed == 0
        assert observer.errors == 0

    def test_on_file_change_callback(self, temp_config):
        """Test on_file_change callback"""
        observer = MemoryObserver(config_path=temp_config)

        # Create a test file
        watch_dir = Path(observer.config['watch']['dirs'][0])
        test_file = watch_dir / 'test.md'
        test_file.write_text('# Test')

        # Call callback
        observer.on_file_change(test_file, 'created')

        # Verify
        assert observer.files_processed == 1
        assert observer.errors == 0

    def test_detect_category(self, temp_config):
        """Test category detection"""
        observer = MemoryObserver(config_path=temp_config)

        test_path = Path('~/Projects/MyProject/notes.md')
        category = observer._detect_category(test_path)
        assert category == 'projects'

    def test_error_handling_in_callback(self, temp_config):
        """Test error handling in on_file_change"""
        observer = MemoryObserver(config_path=temp_config)

        # Try to process non-existent file
        observer.on_file_change(Path('/nonexistent/file.md'), 'created')

        # Should increment errors, not crash
        assert observer.errors == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
PYTHON
```

작성 후 테스트 실행:
```bash
source venv/bin/activate
pytest tests/test_memory_observer.py -v
```

---

## 📊 Phase 2 테스트 체크리스트

### 실제 작동 검증
- [ ] **1-1**: FileWatcher 실제 작동 테스트
  - [ ] 파일 생성 이벤트 감지
  - [ ] 파일 수정 이벤트 감지
  - [ ] 콜백 함수 호출 확인

- [ ] **1-2**: MemoryWriter 파일 복사
  - [ ] 파일 복사 성공
  - [ ] 메타데이터 추가
  - [ ] 내용 일치 확인

### 통합 테스트
- [ ] **2-1**: 데몬 시작/중지
  - [ ] 정상 시작
  - [ ] 설정 로드 성공
  - [ ] Ctrl+C 정상 종료

- [ ] **2-2**: E2E 동기화
  - [ ] 파일 생성 감지
  - [ ] 메모리 디렉토리 동기화
  - [ ] 통계 업데이트

### 에러 처리
- [ ] **3-1**: 잘못된 경로 처리
- [ ] **3-2**: 권한 부족 처리

### Unit Test
- [ ] **4-1**: test_memory_observer.py 작성
- [ ] **4-2**: 모든 테스트 통과

---

## 🎯 Phase 2 완료 기준

| 항목 | 기준 | 상태 |
|------|------|------|
| 실제 작동 테스트 | 2/2 완료 | ⏳ |
| 통합 테스트 | 2/2 완료 | ⏳ |
| Unit Test | 100% 통과 | ⏳ |
| 에러 처리 | 모두 처리 | ⏳ |
| 문서화 | 완료 | ⏳ |

---

## 📝 테스트 실행 일정

```
Day 1 (Priority 1)
  ├─ 1-1: FileWatcher 작동 테스트 (30분)
  └─ 1-2: MemoryWriter 파일 복사 (30분)

Day 2 (Priority 2)
  ├─ 2-1: 데몬 시작/중지 (20분)
  └─ 2-2: E2E 동기화 테스트 (40분)

Day 3 (Priority 3)
  ├─ 3-1: 에러 처리 (20분)
  ├─ 3-2: 권한 처리 (20분)
  └─ 4: Unit Test 작성 (30분)
```

---

## 💡 주의사항

1. **로그 모니터링**: `tail -f oc-memory.log` 사용
2. **메모리 정리**: 테스트 후 `~/.openclaw/workspace/memory` 정리
3. **프로세스 정리**: `pkill -f memory_observer` 필요시
4. **타이밍**: 파일 감시는 1-2초 지연 예상

---

**다음 단계**: Phase 2 실제 테스트 절차 수행
