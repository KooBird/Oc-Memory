# 📚 OC-Memory 다음 테스트 진행 절차

**작성일**: 2026-02-12
**현재 상태**: Phase 1 완료 (66개 Unit Test, 77% 커버리지)
**다음 단계**: Phase 2 통합 테스트

---

## 🎯 전체 진행 절차

```
Phase 1 (✅ 완료)
├─ 66개 Unit Test 작성
├─ 77% 코드 커버리지
└─ config, file_watcher, memory_writer 모듈 검증

Phase 2 (🔴 시작 예정)
├─ 실제 작동 검증
├─ memory_observer.py 통합 테스트
├─ E2E 동기화 검증
└─ test_memory_observer.py 작성

Phase 3 (📅 나중)
├─ OpenClaw 연동
├─ 메모리 시스템 통합
└─ 프로덕션 검증
```

---

## 🚀 Phase 2 빠른 시작 (추천)

**시간**: ~20분 | **난이도**: ⭐⭐

### Step 1️⃣: 빠른 테스트 (5분)
```bash
cd ~/Documents/GitHub/Oc-Memory
source venv/bin/activate

# QUICKSTART_PHASE2.md의 Test 1-3 순서대로 실행
cat QUICKSTART_PHASE2.md
```

**무엇을 확인**:
- FileWatcher가 파일 변경 감지
- MemoryWriter가 파일 복사
- memory_observer가 정상 작동

---

### Step 2️⃣: 상세 테스트 (15분)
```bash
# 상세 테스트 계획 확인
cat PHASE2_TEST_PLAN.md

# Priority 1 테스트 수행
# - 1-1: FileWatcher 실제 작동 테스트
# - 1-2: MemoryWriter 파일 복사 테스트
```

**체크리스트**:
- [ ] FileWatcher 이벤트 감지 3개 이상
- [ ] MemoryWriter 파일 복사 성공
- [ ] metadata 추가 성공

---

## 📋 Phase 2 상세 절차

### 우선순위 1️⃣: 필수 테스트

#### Test 1-1: FileWatcher 실제 작동
```bash
# 터미널 1: 테스트 시작
source venv/bin/activate
python << 'PYTHON'
from lib.file_watcher import FileWatcher
import time

events = []
def callback(file_path, event_type):
    events.append((str(file_path.name), event_type))
    print(f"✅ {event_type}: {file_path.name}")

watcher = FileWatcher(['~/Documents/notes'], callback)
print("🚀 Waiting for events...")
watcher.start()

try:
    for i in range(10):
        print(f"  {i+1}...", end=' ', flush=True)
        time.sleep(1)
except KeyboardInterrupt:
    pass

watcher.stop()
print(f"\n📊 Captured {len(events)} events")
PYTHON

# 터미널 2: 파일 수정 (위 테스트 실행 중)
sleep 3
touch ~/Documents/notes/new_file.md
echo "# Updated" >> ~/Documents/notes/test.md
```

**체크**:
- ✅ 2개 이상 이벤트 감지
- ✅ 파일명 정확
- ✅ 이벤트 타입 정확 (created/modified)

---

#### Test 1-2: MemoryWriter 파일 복사
```bash
source venv/bin/activate

python << 'PYTHON'
from lib.config import get_config
from lib.memory_writer import MemoryWriter
from pathlib import Path

config = get_config('config.yaml')
writer = MemoryWriter(config['memory']['dir'])

test_file = Path('~/Documents/notes/test.md').expanduser()
target = writer.copy_to_memory(test_file, category='notes')

print(f"✅ Source: {test_file}")
print(f"✅ Target: {target}")
print(f"✅ Exists: {target.exists()}")

writer.add_metadata(target, {'copied': 'true'})
print(f"✅ Metadata added")
PYTHON
```

**체크**:
- ✅ 파일 복사 성공
- ✅ 메타데이터 추가
- ✅ 파일 내용 일치

---

### 우선순위 2️⃣: 통합 테스트

#### Test 2-1: memory_observer 시작/종료
```bash
# 터미널 1: 데몬 시작
source venv/bin/activate
python memory_observer.py

# 예상: 정상 시작 로그 출력
# Ctrl+C: 정상 종료
```

**체크**:
- ✅ 정상 시작
- ✅ 설정 로드 성공
- ✅ 깔끔한 종료

---

#### Test 2-2: E2E 동기화 (실제 작동 검증)
```bash
# 터미널 1: memory_observer 시작
source venv/bin/activate
python memory_observer.py

# 터미널 2: 로그 모니터링
tail -f oc-memory.log

# 터미널 3: 파일 생성/수정
sleep 2
echo "# Integration test" > ~/Documents/notes/e2e_test.md
sleep 2
echo "# Updated" >> ~/Documents/notes/e2e_test.md
```

**로그 확인**:
```
[INFO] Processing file: ... (created)
[INFO] Synced to memory: ... (total: 1)
[INFO] Processing file: ... (modified)
[INFO] Synced to memory: ... (total: 2)
```

**체크**:
- ✅ 파일 생성 감지
- ✅ 메모리 동기화
- ✅ 통계 업데이트

---

### 우선순위 3️⃣: Unit Test 작성

#### Test 4: test_memory_observer.py
```bash
# PHASE2_TEST_PLAN.md의 "Phase 2 Unit Test 작성" 섹션 참고

# 파일 생성
cat > tests/test_memory_observer.py << 'EOF'
# (내용은 PHASE2_TEST_PLAN.md 참고)
EOF

# 테스트 실행
source venv/bin/activate
pytest tests/test_memory_observer.py -v
```

---

## 📊 진행 상황 추적

### Phase 2 체크리스트
- [ ] **Test 1-1**: FileWatcher 실제 작동
- [ ] **Test 1-2**: MemoryWriter 파일 복사
- [ ] **Test 2-1**: memory_observer 시작/종료
- [ ] **Test 2-2**: E2E 동기화
- [ ] **Test 3**: 에러 처리
- [ ] **Test 4**: Unit Test 작성

### 완료 기준
- [ ] 모든 테스트 통과
- [ ] Unit Test 100% 통과
- [ ] 통합 테스트 검증 완료
- [ ] 문서 업데이트

---

## 📚 관련 문서

| 문서 | 내용 | 읽는 시간 |
|------|------|---------|
| **QUICKSTART_PHASE2.md** | 빠른 시작 가이드 | 5분 |
| **PHASE2_TEST_PLAN.md** | 상세 테스트 계획 | 20분 |
| **TESTING.md** | 테스트 실행 가이드 | 10분 |
| **TEST_REPORT_PHASE1_2026_02_12.md** | Phase 1 결과 | 10분 |

---

## 💻 명령어 빠른 참고

```bash
# 환경 준비
source venv/bin/activate

# Phase 1 테스트 재실행
pytest tests/ -v

# Phase 2 빠른 테스트
cat QUICKSTART_PHASE2.md

# 로그 확인
tail -f oc-memory.log

# 메모리 디렉토리 확인
find ~/.openclaw/workspace/memory -type f -name "*.md"

# memory_observer 시작
python memory_observer.py

# 프로세스 종료
pkill -f memory_observer
```

---

## 🎯 테스트별 예상 시간

| 테스트 | 준비 | 실행 | 검증 | 합계 |
|--------|------|------|------|------|
| Test 1-1 (FileWatcher) | 2분 | 3분 | 2분 | **7분** |
| Test 1-2 (MemoryWriter) | 1분 | 1분 | 1분 | **3분** |
| Test 2-1 (시작/종료) | 1분 | 2분 | 1분 | **4분** |
| Test 2-2 (E2E) | 2분 | 3분 | 2분 | **7분** |
| Test 3 (에러처리) | 1분 | 2분 | 1분 | **4분** |
| Test 4 (Unit Test) | 5분 | 2분 | 3분 | **10분** |
| **합계** | | | | **~35분** |

---

## ⚠️ 주의사항

1. **먼저 준비**: Phase 1 Unit Test 이해 필수
2. **디렉토리**: ~/Documents/notes 반드시 생성
3. **설정**: config.yaml 생성 필수
4. **타이밍**: 파일 감시 1-2초 지연 예상
5. **로그**: oc-memory.log 확인으로 디버깅

---

## 🆘 문제 해결

### 파일이 감지되지 않음
```bash
# 1. 디렉토리 확인
ls ~/Documents/notes/

# 2. 권한 확인
stat ~/Documents/notes/

# 3. 타이밍 증가
# (테스트 대기 시간 2초 → 5초)
```

### Memory 디렉토리에 파일 없음
```bash
# 1. 디렉토리 확인
mkdir -p ~/.openclaw/workspace/memory

# 2. 권한 확인
chmod 755 ~/.openclaw/workspace/memory

# 3. 설정 확인
cat config.yaml | grep memory
```

### memory_observer 시작 실패
```bash
# 1. config.yaml 확인
cat config.yaml

# 2. Python 환경 확인
python -c "from lib.config import get_config; print('OK')"

# 3. 로그 확인
cat oc-memory.log
```

---

## 🎉 완료 후 다음 단계

Phase 2 테스트 완료 후:

1. **결과 정리**: 테스트 결과 리포트 작성
2. **Phase 3 계획**: OpenClaw 연동 계획
3. **문서화**: 발견 사항 정리
4. **Git 커밋**: 모든 변경사항 커밋

---

## 📞 필요시 참고

```bash
# Phase 1 테스트 재확인
pytest tests/ --cov=lib --cov-report=term-missing

# 설정 검증
python -c "from lib.config import get_config; import pprint; pprint.pprint(get_config())"

# FileWatcher 독립 테스트
python lib/file_watcher.py

# MemoryWriter 독립 테스트
python lib/memory_writer.py
```

---

**준비 완료! 위 절차를 따라 Phase 2 테스트를 진행하세요.** 🚀

**추천 시작**: QUICKSTART_PHASE2.md부터 시작하기!
