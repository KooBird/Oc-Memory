# 🚀 Phase 4: 프로덕션 배포 준비

**시작일**: 2026-02-12 23:40
**목표**: 프로덕션 환경 준비 완료
**예상 시간**: 1시간
**최종 상태**: 배포 준비 완료

---

## 📋 Phase 4 작업 체크리스트

### 1️⃣ 성능 최적화 (15분)

#### 1-1: 대량 파일 처리 테스트
```bash
# 100개의 테스트 파일 생성
for i in {1..100}; do
  echo "# Test $i" > ~/Documents/notes/test_$i.md
done

# FileWatcher 성능 테스트
time python memory_observer.py  # 처리 시간 측정
```

**목표**:
- 100개 파일 <10초 처리
- 메모리 사용 <100MB
- CPU 사용 <50%

#### 1-2: 메모리 누수 테스트
```python
# memory_observer.py를 1시간 실행
# 메모리 사용 모니터링
import psutil
import time

process = psutil.Process()
for _ in range(60):
    print(f"Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB")
    time.sleep(60)
```

---

### 2️⃣ 설정 파일 정리 (10분)

#### 2-1: config.yaml 최적화
```yaml
# 프로덕션 설정 예시
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
  level: INFO  # 프로덕션: INFO (DEBUG 제외)
  file: ~/.openclaw/logs/oc-memory.log
  console: false  # 백그라운드에서는 false

hot_memory:
  ttl_days: 90
  max_observations: 50000

llm:
  enabled: false  # 필요시만 활성화
```

#### 2-2: 환경 변수 설정
```bash
# .env 파일 생성
cat > .env << 'EOF'
# OC-Memory Configuration
OC_MEMORY_LOG_LEVEL=INFO
OC_MEMORY_CONFIG_PATH=~/.openclaw/config.yaml
OC_MEMORY_DATA_DIR=~/.openclaw/workspace/memory
EOF
```

---

### 3️⃣ 에러 처리 강화 (20분)

#### 3-1: 예외 처리 개선
```python
# lib/memory_observer.py에서
class MemoryObserverError(Exception):
    """MemoryObserver 에러"""
    pass

class ErrorRecovery:
    def __init__(self):
        self.retry_count = 0
        self.max_retries = 3

    def retry_on_error(self, func, *args, **kwargs):
        """에러 발생 시 재시도"""
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self.retry_count += 1
                logging.error(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # 지수 백오프
                else:
                    raise
```

#### 3-2: 파일 권한 처리
```python
# 파일 접근 불가 처리
try:
    with open(file_path) as f:
        content = f.read()
except PermissionError:
    logging.warning(f"Permission denied: {file_path}")
    # 대체 동작 수행
except FileNotFoundError:
    logging.error(f"File not found: {file_path}")
    # 재시도 또는 스킵
```

---

### 4️⃣ 로깅 및 모니터링 (15분)

#### 4-1: 구조화된 로깅
```python
import logging
from pythonjsonlogger import jsonlogger

# JSON 로그 포맷
logger = logging.getLogger(__name__)
handler = logging.FileHandler('oc-memory.log')
formatter = jsonlogger.JsonFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)

# 사용 예
logger.info("File processed", extra={
    "file": file_path,
    "event": "created",
    "category": "notes",
    "duration_ms": 123
})
```

#### 4-2: 성능 메트릭
```python
import time

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            'total_files': 0,
            'total_errors': 0,
            'avg_processing_time': 0,
            'peak_memory': 0,
        }

    def record_processing(self, duration_ms, file_size):
        self.metrics['total_files'] += 1
        self.metrics['avg_processing_time'] = (
            (self.metrics['avg_processing_time'] + duration_ms) / 2
        )
        logging.info("Processing completed", extra=self.metrics)
```

#### 4-3: 헬스 체크
```python
def health_check():
    """시스템 상태 확인"""
    checks = {
        'file_watcher': watcher.is_alive(),
        'memory_writer': memory_dir.exists(),
        'disk_space': get_disk_space() > 100_000_000,  # 100MB
        'last_update': get_last_update_time(),
    }

    if all(checks.values()):
        logging.info("Health check: OK")
        return True
    else:
        logging.error("Health check failed", extra=checks)
        return False
```

---

### 5️⃣ CI/CD 파이프라인 (20분)

#### 5-1: GitHub Actions 워크플로우
```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Run tests
        run: pytest tests/ --cov=lib --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

#### 5-2: 배포 체크리스트
```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  release:
    types: [created]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run tests
        run: pytest tests/ -v

      - name: Check coverage
        run: pytest tests/ --cov=lib --cov-fail-under=75

      - name: Build distribution
        run: python -m build

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
```

---

## 🔧 Phase 4 상세 진행 절차

### Step 1: 성능 최적화 테스트 (실행)

```bash
# 1-1: 100개 파일 생성 및 처리
mkdir -p ~/Documents/notes
for i in {1..100}; do echo "# Test $i" > ~/Documents/notes/test_$i.md; done

# 1-2: memory_observer 성능 테스트
time python memory_observer.py  # 3초 이내 완료 목표
```

### Step 2: 설정 파일 최적화 (실행)

```bash
# 프로덕션 config.yaml 확인
cat config.yaml

# .env 파일 생성
cat > .env << 'EOF'
OC_MEMORY_LOG_LEVEL=INFO
OC_MEMORY_CONFIG_PATH=~/.openclaw/config.yaml
EOF
```

### Step 3: 에러 처리 강화 (검토)

```bash
# 예외 상황 테스트
# 1. 읽기 전용 파일
# 2. 권한 없는 디렉토리
# 3. 디스크 부족
# 4. 메모리 부족
```

### Step 4: 로깅 설정 (구성)

```bash
# requirements.txt에 추가
pip install python-json-logger

# 로그 설정 확인
grep -A 10 "logging" config.yaml
```

### Step 5: CI/CD 파이프라인 (준비)

```bash
# GitHub Actions 워크플로우 생성
mkdir -p .github/workflows

# test.yml 생성
cat > .github/workflows/test.yml << 'EOF'
# (위의 yaml 내용)
EOF
```

---

## 📊 Phase 4 진행 추적

### 진행 현황
```
□ 1️⃣  성능 최적화
  □ 대량 파일 처리 테스트
  □ 메모리 누수 테스트
  □ 응답 시간 측정

□ 2️⃣  설정 파일 정리
  □ config.yaml 최적화
  □ 환경 변수 설정
  □ 프로덕션 설정 확인

□ 3️⃣  에러 처리 강화
  □ 예외 처리 개선
  □ 파일 권한 처리
  □ 재시도 로직 추가

□ 4️⃣  로깅 및 모니터링
  □ 구조화된 로깅
  □ 성능 메트릭
  □ 헬스 체크

□ 5️⃣  CI/CD 파이프라인
  □ GitHub Actions 설정
  □ 자동 테스트
  □ 자동 배포
```

---

## 🎯 Phase 4 완료 기준

- [x] 단위 테스트 66개 모두 통과
- [x] 통합 테스트 3개 모두 통과
- [x] OpenClaw 연동 완료
- [ ] 성능 테스트 통과 (100개 파일 <10초)
- [ ] 에러 처리 100% 커버
- [ ] 로깅 및 모니터링 구성
- [ ] CI/CD 파이프라인 구축
- [ ] 프로덕션 배포 체크리스트 작성

---

## 📈 전체 프로젝트 진행률

```
Phase 1: ████████████████████ 100% ✅
Phase 2: ████████████████████ 100% ✅
Phase 3: ████████████████████ 100% ✅
Phase 4: ░░░░░░░░░░░░░░░░░░░░ 0% 🔴 (진행 중)

━━━━━━━━━━━━━━━━━━━━━━━━━━━
전체: ████████████████░░░░░░ 75% → 85% 목표
```

---

## 💡 주의사항

1. **프로덕션 환경**
   - 로그 레벨을 INFO로 설정 (DEBUG 제외)
   - 콘솔 출력 비활성화 (백그라운드 실행)
   - 파일 크기 제한 설정

2. **성능 최적화**
   - 대량 파일 처리 시 배치 처리
   - 메모리 캐시 크기 제한
   - 주기적인 정리 작업

3. **에러 복구**
   - 재시도 로직 지수 백오프
   - 에러 로깅 상세
   - 자동 복구 시도

4. **모니터링**
   - 매 1시간마다 헬스 체크
   - 메모리 누수 감시
   - 처리 시간 추적

---

**Phase 4 준비 완료! 시작하시겠습니까?** 🚀
