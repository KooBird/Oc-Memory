# 🚀 Phase 2 테스트 빠른 시작 가이드

Phase 2 테스트를 5분 안에 시작할 수 있는 간단한 가이드입니다.

---

## 📋 필수 준비

```bash
# 1. 가상 환경 활성화
source venv/bin/activate

# 2. 감시 디렉토리 생성
mkdir -p ~/Documents/notes
mkdir -p ~/Projects

# 3. 테스트 파일 생성
echo "# Test Note" > ~/Documents/notes/test.md
```

---

## 🧪 Test 1: FileWatcher 실제 작동 (5분)

**목표**: 파일 변경을 실시간으로 감지하는지 확인

### 터미널 1: FileWatcher 테스트 시작
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

### 터미널 2: 파일 생성/수정 (스크립트 실행 중)
```bash
# 3초 대기 후 실행
sleep 3

# 파일 생성
touch ~/Documents/notes/new_file.md

# 파일 수정
echo "# Updated" >> ~/Documents/notes/test.md

# 파일 생성
echo "# Another file" > ~/Documents/notes/another.md
```

**예상 결과**:
```
✅ created: new_file.md
✅ modified: test.md
✅ created: another.md

📊 Captured 3 events:
  created: new_file.md
  modified: test.md
  created: another.md
```

✅ **성공 기준**: 3개 이상의 이벤트 감지

---

## 🧪 Test 2: MemoryWriter 파일 복사 (3분)

**목표**: 파일이 메모리 디렉토리에 정상 복사되는지 확인

```bash
source venv/bin/activate

python << 'PYTHON'
from lib.config import get_config
from lib.memory_writer import MemoryWriter
from pathlib import Path

# 설정 로드
config = get_config('config.yaml')

# MemoryWriter 초기화
writer = MemoryWriter(config['memory']['dir'])

# 테스트 파일 준비
test_file = Path('~/Documents/notes/test.md').expanduser()

print(f"📄 Source: {test_file}")
print(f"  Exists: {test_file.exists()}")

# 파일 복사
category = writer.get_category_from_path(test_file)
print(f"🏷️  Category: {category}")

target = writer.copy_to_memory(test_file, category=category)
print(f"✅ Copied to: {target}")

# 메타데이터 추가
from datetime import datetime
writer.add_metadata(target, {
    'source': str(test_file),
    'copied_at': datetime.now().isoformat()
})
print(f"✅ Metadata added")

# 검증
assert target.exists(), "Target not found!"
print(f"✅ Verification passed!")

# 메모리 디렉토리 확인
import os
memory_dir = Path(config['memory']['dir'])
files = list(memory_dir.rglob('*.md'))
print(f"\n📁 Memory directory files: {len(files)}")
for f in files[:5]:
    print(f"  {f.relative_to(memory_dir)}")
PYTHON
```

**예상 결과**:
```
📄 Source: /Users/.../Documents/notes/test.md
  Exists: True
🏷️  Category: notes
✅ Copied to: /Users/.../.openclaw/workspace/memory/notes/test.md
✅ Metadata added
✅ Verification passed!

📁 Memory directory files: 1
  notes/test.md
```

✅ **성공 기준**: 파일 복사 및 메타데이터 추가 성공

---

## 🧪 Test 3: memory_observer.py 데몬 테스트 (5분)

**목표**: memory_observer 데몬이 정상 시작/종료되는지 확인

### 터미널 1: memory_observer 시작
```bash
source venv/bin/activate
python memory_observer.py
```

**예상 출력**:
```
2026-02-12 10:30:45,123 - root - INFO - ============================================================
2026-02-12 10:30:45,124 - root - INFO - Starting OC-Memory Observer
2026-02-12 10:30:45,125 - root - INFO - ============================================================
2026-02-12 10:30:45,126 - root - INFO - Watch directories: ['/Users/.../Documents/notes', ...]
2026-02-12 10:30:45,127 - root - INFO - Memory directory: /Users/.../.openclaw/workspace/memory
2026-02-12 10:30:45,128 - root - INFO - ============================================================
2026-02-12 10:30:45,129 - root - INFO - OC-Memory Observer started successfully
2026-02-12 10:30:45,130 - root - INFO - Monitoring for file changes... (Press Ctrl+C to stop)
```

### 터미널 2: 파일 생성 (daemon 실행 중)
```bash
# 2초 대기
sleep 2

# 테스트 파일 생성
echo "# Integration test" > ~/Documents/notes/integration_test.md

echo "✅ File created"
sleep 2
```

### 터미널 1에서 로그 확인
```
2026-02-12 10:30:47,200 - lib.file_watcher - INFO - New markdown file detected: .../integration_test.md
2026-02-12 10:30:47,201 - memory_observer - INFO - Processing file: .../integration_test.md (created)
2026-02-12 10:30:47,202 - memory_observer - INFO - Synced to memory: .../notes/integration_test.md (total: 1)
```

### 터미널 1: Ctrl+C로 종료
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

✅ **성공 기준**: 정상 시작, 파일 동기화, 깔끔한 종료

---

## 🔍 로그 확인

```bash
# 로그 파일 확인
tail -100 oc-memory.log

# 실시간 로그 모니터링
tail -f oc-memory.log
```

---

## 📊 메모리 디렉토리 확인

```bash
# 메모리 디렉토리 구조 확인
tree ~/.openclaw/workspace/memory/

# 또는
find ~/.openclaw/workspace/memory -type f -name "*.md" | head -10

# 파일 개수 확인
find ~/.openclaw/workspace/memory -type f -name "*.md" | wc -l

# 최근 파일 확인
find ~/.openclaw/workspace/memory -type f -name "*.md" -mtime -1 | sort
```

---

## ⚠️ 문제 해결

### Q: FileWatcher가 파일 변화를 감지하지 못함
```bash
# 디렉토리 확인
ls -la ~/Documents/notes/

# 파일 권한 확인
stat ~/Documents/notes/test.md

# 타이밍 증가 (2초 대신 5초)
```

### Q: MemoryWriter가 파일을 복사하지 못함
```bash
# 메모리 디렉토리 확인
ls -la ~/.openclaw/workspace/memory/

# 권한 확인
stat ~/.openclaw/workspace/memory/

# 부모 디렉토리 생성
mkdir -p ~/.openclaw/workspace/memory
```

### Q: memory_observer가 시작되지 않음
```bash
# config.yaml 확인
cat config.yaml

# Python 패키지 확인
python -c "from lib.config import get_config; print(get_config())"

# 로그 확인
cat oc-memory.log
```

---

## 📈 다음 단계

1. ✅ **Phase 2 Test 1-3 완료**: 실제 작동 검증
2. ➡️ **Unit Test 작성**: test_memory_observer.py 추가
3. ➡️ **에러 처리 테스트**: 예외 상황 검증
4. ➡️ **Phase 3**: OpenClaw 연동

---

## 📚 추가 정보

더 자세한 테스트 계획은 **PHASE2_TEST_PLAN.md**를 참고하세요.

```bash
# Phase 2 테스트 계획 보기
cat PHASE2_TEST_PLAN.md

# 모든 테스트 관련 문서
ls -la *TEST*.md
ls -la PHASE*.md
```

---

**시작하기**: 위 테스트 1-3을 순서대로 실행하세요! 🎉
