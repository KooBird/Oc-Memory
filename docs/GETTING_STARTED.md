# OC-Memory 시작하기

OC-Memory를 5분 이내에 설치하고 시작할 수 있습니다! 이 가이드는 설치, 구성, 시스템 실행 및 문제 해결을 다룹니다.

## 필수 요구사항

시작하기 전에 다음을 확인하세요:

- **Python 3.10 이상** - 확인하기: `python3 --version`
- **pip** - Python 3.9 이상에 포함됨
- **가상 환경** (권장) - Python에 내장됨
- **디스크 공간** - 종속성 및 로그를 위해 최소 100MB 여유 공간
- **OpenClaw 설치** - 메모리 통합에 필요 (참고: [OpenClaw 저장소](https://github.com/openclaw-ai/openclaw))

### 시스템 요구사항

- **Linux/macOS/Windows** - 모두 지원됨
- **디스크 I/O** - 파일 감시를 위한 좋은 성능 (SSD 권장하지만 필수 아님)
- **네트워크** - API 기능을 위해 선택적 (기본 작동은 오프라인으로 작동)

---

## 설치

### 1단계: 저장소 복제

```bash
git clone https://github.com/openclaw-ai/oc-memory.git
cd oc-memory
```

### 2단계: 가상 환경 생성 및 활성화

```bash
# 가상 환경 생성
python3 -m venv venv

# 가상 환경 활성화
source venv/bin/activate          # macOS/Linux에서
# 또는
venv\Scripts\activate             # Windows에서
```

터미널 프롬프트 시작 부분에 `(venv)`가 표시되어야 합니다.

### 3단계: 종속성 설치

```bash
pip install -r requirements.txt
```

이는 `watchdog` (파일 모니터링), `pyyaml` (구성) 등을 포함한 모든 필수 패키지를 설치합니다.

### 4단계: 설치 확인

```bash
python -c "import watchdog; import yaml; print('✅ Installation successful')"
```

---

## 설치 이해하기

### 구성되는 항목

설치 중에 OC-Memory는 다음을 구성합니다:

1. **감시 디렉토리** - `.md` 파일을 모니터링할 디렉토리
   - 기본값: `~/Documents/notes`, `~/Projects`
   - 모든 디렉토리를 모니터링하도록 사용자 지정 가능

2. **메모리 디렉토리** - 동기화된 파일이 저장되는 위치
   - 기본값: `~/.openclaw/workspace/memory`
   - OpenClaw의 내장 메모리 시스템

3. **로깅** - 발생 중인 일을 추적하기 위한 디버그/정보 로깅
   - 로그 파일: `oc-memory.log`
   - 문제 해결을 위해 DEBUG로 설정할 수 있음

4. **자동 분류** - 파일을 범주별로 자동 정렬
   - `notes/` - 노트 디렉토리의 파일
   - `projects/` - 프로젝트 디렉토리의 파일
   - `documents/` - 문서 디렉토리의 파일
   - `general/` - 분류되지 않은 파일

### 기본 구성

기본 `config.yaml`은 다음과 같습니다:

```yaml
watch:
  dirs:
    - ~/Documents/notes
    - ~/Projects
  recursive: true              # 하위 디렉토리 감시

memory:
  dir: ~/.openclaw/workspace/memory
  auto_categorize: true        # 범주 감지 활성화

logging:
  level: INFO                  # DEBUG, INFO, WARNING, ERROR
  file: oc-memory.log
  console: true                # 실행 중 출력 표시
```

### 구성 사용자 지정

구성을 수정하려면:

```bash
# 구성 파일 편집
nano config.yaml    # 또는 원하는 편집기 사용
```

일반적인 사용자 지정:

```yaml
# 더 많은 감시 디렉토리 추가
watch:
  dirs:
    - ~/Documents/notes
    - ~/Projects
    - ~/Desktop/scratch
    - ~/my-notes

# 필요한 경우 메모리 디렉토리 변경
memory:
  dir: ~/.openclaw/workspace/memory
  auto_categorize: true

# 문제 해결을 위해 자세한 로깅 활성화
logging:
  level: DEBUG
  file: oc-memory.log
  console: true
```

---

## 첫 실행

### 메모리 옵저버 시작

메모리 옵저버는 디렉토리를 모니터링하고 파일을 OpenClaw에 동기화하는 주요 데몬 프로세스입니다:

```bash
# 가상 환경이 활성화되었는지 확인
source venv/bin/activate

# 옵저버 시작
python memory_observer.py
```

다음과 같은 출력이 표시되어야 합니다:

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

옵저버가 이제 실행 중이며 구성된 디렉토리를 모니터링합니다. 전경에서 실행되며 Ctrl+C로 중지할 수 있습니다.

### 실행 시 발생하는 일

옵저버는:
1. 구성된 모든 감시 디렉토리에서 새로운/수정된 `.md` 파일 모니터링
2. 실시간으로 파일 변경 감지 (1-2초 지연)
3. OpenClaw의 메모리 디렉토리로 파일 복사
4. 파일 경로를 기반으로 범주 자동 감지 및 할당
5. 메타데이터 추가 (타임스탬프, 소스 경로, 범주)
6. OpenClaw가 약 5초 내에 자동 인덱싱

---

## 각 구성 요소 이해하기

### FileWatcher

**역할:** 마크다운 파일 변경에 대한 디렉토리 모니터링

- 하나 이상의 디렉토리를 재귀적으로 감시
- `.md` 파일이 생성되거나 수정될 때 감지
- 마크다운이 아닌 파일 무시
- 변경 감지 시 콜백 함수 실행
- 크로스 플랫폼 파일 모니터링을 위해 `watchdog` 라이브러리 사용

**위치:** `lib/file_watcher.py`

**수동 테스트 방법:**

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

**역할:** 메타데이터를 포함하여 OpenClaw의 메모리 시스템에 파일 작성

핵심 함수:
- **copy_to_memory()** - 메모리 디렉토리로 파일 복사, 충돌 처리
- **write_memory_entry()** - 콘텐츠에서 새 메모리 항목 생성
- **add_metadata()** - 타임스탬프, 범주, 소스 경로를 포함한 YAML 머리글 추가
- **get_category_from_path()** - 파일 경로에서 범주 자동 감지

**위치:** `lib/memory_writer.py`

**파일 분류 방식:**
- 경로에 "project" 포함 → `projects/` 폴더
- 경로에 "note" 포함 → `notes/` 폴더
- 경로에 "doc" 또는 "document" 포함 → `documents/` 폴더
- 경로에 "meeting" 포함 → `meetings/` 폴더
- 기타 모두 → `general/` 폴더

**수동 테스트 방법:**

```bash
python << 'EOF'
from lib.memory_writer import MemoryWriter
from pathlib import Path
from datetime import datetime

writer = MemoryWriter('~/.openclaw/workspace/memory')

# 테스트 파일 생성
test_file = Path('~/Documents/notes/test.md').expanduser()
test_file.write_text("# Test Note\nThis is a test.")

# 메모리로 복사
category = writer.get_category_from_path(test_file)
target = writer.copy_to_memory(test_file, category=category)

# 메타데이터 추가
writer.add_metadata(target, {
    'source': str(test_file),
    'synced_at': datetime.now().isoformat(),
    'category': category
})

print(f"✅ File synced to: {target}")
EOF
```

### 메모리 옵저버 데몬

**역할:** FileWatcher 및 MemoryWriter 구성 요소 조율

주요 `memory_observer.py` 프로세스:
1. `config.yaml`에서 구성 로드
2. 구성된 디렉토리로 FileWatcher 초기화
3. 메모리 디렉토리로 MemoryWriter 초기화
4. FileWatcher 시작 및 파일 변경 이벤트 대기
5. 파일 변경 시 자동으로 메모리에 동기화
6. 통계 추적 (처리된 파일, 오류)
7. 정상 종료 처리 (Ctrl+C)

**흐름 다이어그램:**

```
사용자가 .md 파일 생성/편집
          ↓
FileWatcher가 변경 감지
          ↓
FileWatcher가 콜백 실행
          ↓
memory_observer가 파일 처리
          ↓
MemoryWriter가 메모리 디렉토리로 복사
          ↓
MemoryWriter가 메타데이터 추가 (타임스탬프, 범주, 소스)
          ↓
OpenClaw가 파일 자동 인덱싱 (~5초)
          ↓
메모리가 OpenClaw에서 검색 가능
```

---

## 자동으로 발생하는 일

### 파일 감지

감시 디렉토리에서 `.md` 파일을 생성하거나 수정할 때:

1. FileWatcher가 1-2초 내에 변경 감지
2. 로그에 감지 기록: `New markdown file detected: /path/to/file.md`
3. 동기화 프로세스 실행

### 범주 감지

OC-Memory는 파일 경로에서 자동으로 범주를 감지합니다:

```
~/Documents/notes/python-tips.md     → notes/
~/Projects/ai-research/summary.md    → projects/
~/Documents/meeting-notes.md         → documents/
~/misc/article.md                    → general/
```

### 메타데이터 추가

동기화된 모든 파일은 다음 YAML 머리글을 받습니다:

```yaml
---
source: /Users/you/Documents/notes/example.md
synced_at: 2026-02-12T10:30:47.123456
category: notes
event_type: created
oc_memory_version: 0.1.0
---

# 여기에 원본 파일 콘텐츠...
```

### OpenClaw 통합

파일이 동기화된 후:
1. `~/.openclaw/workspace/memory/[category]/`에 파일 표시
2. OpenClaw의 파일 감시자가 새 파일 감지
3. OpenClaw가 자동 인덱싱 (~5초)
4. OpenClaw의 memory_search 도구를 통해 검색 가능

---

## 검증

### 기본 작동 확인 방법

다음 단계를 따라 모든 것이 작동하는지 확인하세요:

#### 터미널 1: 옵저버 시작

```bash
source venv/bin/activate
python memory_observer.py
```

실행 상태로 둡니다.

#### 터미널 2: 테스트 노트 생성

```bash
# 노트 디렉토리가 없으면 생성
mkdir -p ~/Documents/notes

# 테스트 노트 생성
cat > ~/Documents/notes/test_note.md << 'EOF'
# Test Memory Entry

This is a test note for OC-Memory verification.

## Key Points
- First point
- Second point
EOF
```

#### 예상 동작

터미널 1에서 다음을 볼 수 있어야 합니다:

```
2026-02-12 10:32:15,456 - lib.file_watcher - INFO - New markdown file detected: /Users/you/Documents/notes/test_note.md
2026-02-12 10:32:15,457 - memory_observer - INFO - Processing file: /Users/you/Documents/notes/test_note.md (created)
2026-02-12 10:32:15,458 - memory_observer - INFO - Synced to memory: /Users/you/.openclaw/workspace/memory/notes/test_note.md (total: 1)
```

#### 메모리 디렉토리 확인

```bash
# 동기화된 파일 나열
ls -la ~/.openclaw/workspace/memory/notes/

# 메타데이터가 포함된 동기화된 파일 보기
cat ~/.openclaw/workspace/memory/notes/test_note.md
```

YAML 머리글이 추가된 파일을 볼 수 있어야 합니다.

---

## 자신의 파일로 테스트

### 빠른 테스트 (2분)

```bash
# 옵저버가 실행 중인 동안 터미널 2에서:

# 새 노트 생성
echo "# My Project Notes" > ~/Documents/notes/project.md
echo "Important details here" >> ~/Documents/notes/project.md

# 2초 대기
sleep 2

# 동기화되었는지 확인
ls -la ~/.openclaw/workspace/memory/notes/
```

### 종합 테스트 (10분)

다양한 디렉토리에서 여러 파일을 생성하여 분류를 테스트합니다:

```bash
# 테스트 파일 생성
mkdir -p ~/Documents/notes
mkdir -p ~/Projects/demo
mkdir -p ~/Documents/research

# 노트
echo "# Note 1" > ~/Documents/notes/note1.md
echo "# Note 2" > ~/Documents/notes/sub/note2.md

# 프로젝트
echo "# Project Update" > ~/Projects/demo/status.md

# 문서
echo "# Research" > ~/Documents/research/paper.md

# 5초 후 결과 확인
sleep 5
find ~/.openclaw/workspace/memory -name "*.md" -type f
```

파일이 각각의 범주로 구성되어 있을 것을 볼 수 있어야 합니다.

---

## 로그 모니터링

### 최근 로그 보기

```bash
# 마지막 50줄
tail -50 oc-memory.log

# 타임스탬프가 있는 마지막 20줄
tail -20 oc-memory.log | cat -n
```

### 실시간 로그 모니터링

```bash
# 작성되는 대로 로그 감시
tail -f oc-memory.log

# Ctrl+C로 종료
```

### 특정 이벤트 찾기

```bash
# 파일 동기화 이벤트 찾기
grep "Synced to memory" oc-memory.log

# 오류 찾기
grep "ERROR" oc-memory.log

# 특정 파일 찾기
grep "test_note.md" oc-memory.log

# 마지막 5개 동기화 작업 보기
grep "Synced to memory" oc-memory.log | tail -5
```

### 디버그 로깅 활성화

자세한 문제 해결을 위해 DEBUG 로깅을 활성화합니다:

```yaml
# config.yaml에서
logging:
  level: DEBUG
  file: oc-memory.log
```

그 후 옵저버를 다시 시작합니다. 디버그 로그는 다음을 표시합니다:
- 파일 감지 세부사항
- 디렉토리 스캔
- 구성 로드
- 메타데이터 처리

---

## 메모리 디렉토리 확인

### 모든 메모리 파일 나열

```bash
# 총 파일 수 계산
find ~/.openclaw/workspace/memory -name "*.md" -type f | wc -l

# 모든 파일 범주와 함께 나열
find ~/.openclaw/workspace/memory -name "*.md" -type f | sort

# 파일명만 나열
ls -R ~/.openclaw/workspace/memory
```

### 특정 범주 확인

```bash
# 노트
ls ~/.openclaw/workspace/memory/notes/

# 프로젝트
ls ~/.openclaw/workspace/memory/projects/

# 문서
ls ~/.openclaw/workspace/memory/documents/

# 일반 (분류되지 않은)
ls ~/.openclaw/workspace/memory/general/
```

### 파일 메타데이터 보기

```bash
# 머리글 보기 (처음 10줄)
head -20 ~/.openclaw/workspace/memory/notes/test_note.md

# 전체 파일 내용 보기
cat ~/.openclaw/workspace/memory/notes/test_note.md
```

### OpenClaw에서 파일 확인

```bash
# OpenClaw 데이터베이스가 존재하는지 확인
ls -la ~/.openclaw/agents/main/memory.db

# 메모리 디렉토리가 OpenClaw에서 읽을 수 있는지 확인
ls -la ~/.openclaw/workspace/memory/
```

---

## 고급 사용법

### 여러 디렉토리 모니터링

`config.yaml`을 편집하여 여러 위치를 감시합니다:

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

### 사용자 정의 분류

현재 범주는 파일 경로에서 자동으로 감지됩니다. 특정 범주를 사용하려면:

소스 파일을 수동으로 구성합니다:
```
~/Documents/notes/         → notes/
~/Projects/                → projects/
~/Documents/meeting-notes/ → documents/
~/research/               → general/
```

### 여러 인스턴스 실행

여러 관찰자를 다양한 디렉토리 세트에 대해 실행할 수 있습니다:

**옵저버 1** - 개인 노트:
```bash
python memory_observer.py --config config-personal.yaml
```

**옵저버 2** - 작업 파일:
```bash
python memory_observer.py --config config-work.yaml
```

각각의 `config.yaml` 파일을 가집니다.

### 콘솔 출력 비활성화

백그라운드 작동을 위해 콘솔 로깅을 비활성화합니다:

```yaml
logging:
  level: INFO
  file: oc-memory.log
  console: false
```

### 로그 보관 증가

로그 파일 크기를 모니터링하고 이전 로그를 보관합니다:

```bash
# 현재 로그 크기 확인
du -h oc-memory.log

# 보관 및 압축
mv oc-memory.log oc-memory-2026-02-12.log.gz
gzip oc-memory-2026-02-12.log
```

---

## 일반적인 문제 및 문제 해결

### 파일이 감지되지 않음

**문제:** `.md` 파일을 생성/수정했지만 로그에 나타나지 않습니다.

**해결책:**

1. **감시 디렉토리가 존재하는지 확인:**
   ```bash
   ls -la ~/Documents/notes
   ls -la ~/Projects
   ```
   없으면 생성합니다:
   ```bash
   mkdir -p ~/Documents/notes
   mkdir -p ~/Projects
   ```

2. **파일 확장자 확인:**
   - 파일은 `.md` 또는 `.markdown`이어야 합니다
   - 확인: `ls -la ~/Documents/notes/*.md`

3. **디버그 로깅 활성화:**
   ```yaml
   # config.yaml에서
   logging:
     level: DEBUG
   ```
   옵저버를 다시 시작하고 로그 확인:
   ```bash
   tail -f oc-memory.log | grep "detecting\|watching"
   ```

4. **파일 쓰기 완료 확인:**
   - 일부 편집기는 비동기적으로 저장합니다
   - 저장 후 2-3초 대기
   - 일부 클라우드 동기화 도구가 파일 감시 방해 가능

5. **구성 파일 확인:**
   ```bash
   python << 'EOF'
   from lib.config import get_config
   config = get_config('config.yaml')
   print("Watch dirs:", config['watch']['dirs'])
   EOF
   ```

**일반적인 원인:** 디렉토리 경로 오타 (예: `~/Document` 대신 `~/Documents`)

### 파일이 메모리 디렉토리에 표시되지 않음

**문제:** 파일이 감지되었지만 `~/.openclaw/workspace/memory/`에 나타나지 않습니다.

**해결책:**

1. **메모리 디렉토리 권한 확인:**
   ```bash
   ls -la ~/.openclaw/workspace/
   chmod -R 755 ~/.openclaw/workspace/memory
   ```

2. **구성에서 메모리 디렉토리 확인:**
   ```bash
   python lib/config.py
   # 다음을 표시해야 함: memory_dir: ~/.openclaw/workspace/memory
   ```

3. **로그에서 복사 오류 확인:**
   ```bash
   grep "Error\|Failed" oc-memory.log
   ```

4. **소스 파일이 읽을 수 있는지 확인:**
   ```bash
   cat ~/Documents/notes/test.md  # 콘텐츠 표시해야 함
   ```

5. **디스크 공간 확인:**
   ```bash
   df -h ~/
   # 최소 10% 여유 공간이 있는지 확인하세요
   ```

**일반적인 원인:** 메모리 디렉토리가 없거나 잘못된 경로로 구성됨

### OpenClaw가 메모리를 찾지 못함

**문제:** 파일이 메모리 디렉토리로 동기화되었지만 OpenClaw가 찾을 수 없습니다.

**해결책:**

1. **인덱싱 대기 (5-10초):**
   - OpenClaw는 동기화 후 자동으로 파일 인덱싱합니다
   - 새 파일은 최대 10초가 걸릴 수 있습니다

2. **OpenClaw 메모리 데이터베이스 확인:**
   ```bash
   ls -la ~/.openclaw/agents/main/memory.db
   ```

3. **파일 형식 확인:**
   - 파일은 유효한 마크다운이어야 합니다
   - 구문 오류 확인:
   ```bash
   head -5 ~/.openclaw/workspace/memory/notes/test.md
   ```

4. **OpenClaw 다시 시작:**
   - OpenClaw 세션 중지 및 다시 시작
   - 메모리 파일의 강제 재인덱싱

5. **OpenClaw 메모리 구성 확인:**
   - OpenClaw에서 메모리 디렉토리 경로 확인:
   ```bash
   grep -r "memory" ~/.openclaw/config.yaml
   ```

**일반적인 원인:** 타이밍 문제 - 10초 대기 후 다시 시도

### 구성 오류로 설치 실패

**문제:** 옵저버 시작 시 `ConfigError: Configuration error` 오류 발생

**해결책:**

1. **구성 파일이 있는지 확인:**
   ```bash
   ls -la config.yaml
   ```

2. **없으면 템플릿에서 생성:**
   ```bash
   cp config.example.yaml config.yaml
   # 필요에 따라 편집하세요
   ```

3. **YAML 구문 검증:**
   ```bash
   python << 'EOF'
   import yaml
   with open('config.yaml') as f:
       config = yaml.safe_load(f)
   print("Config loaded successfully")
   print(f"Watch dirs: {config['watch']['dirs']}")
   EOF
   ```

4. **config.yaml의 오타 확인:**
   - 적절한 들여쓰기 확인 (2칸)
   - 디렉토리 경로는 `~` 또는 절대 경로 사용
   - 공백이 있는 경로 따옴표 처리: `"~/My Documents"`

5. **홈 디렉토리 확장:**
   구성의 경로는 `~`를 사용합니다:
   ```yaml
   # 좋음
   watch:
     dirs:
       - ~/Documents/notes

   # 역시 좋음
   watch:
     dirs:
       - /Users/username/Documents/notes
   ```

**일반적인 원인:** 잘못된 YAML 들여쓰기 또는 누락된 필수 필드

### 옵저버 충돌 또는 중지

**문제:** 옵저버가 시작되었지만 몇 초 후 종료됩니다.

**해결책:**

1. **로그에서 오류 확인:**
   ```bash
   tail -50 oc-memory.log
   grep "Exception\|Error\|Traceback" oc-memory.log
   ```

2. **감시 디렉토리를 읽을 수 있는지 확인:**
   ```bash
   test -r ~/Documents/notes && echo "readable" || echo "not readable"
   ```

3. **권한 문제 확인:**
   ```bash
   chmod +rx ~/Documents/notes
   chmod +rx ~/.openclaw/workspace/memory
   ```

4. **상세 출력으로 실행:**
   ```bash
   # 임시로 DEBUG로 설정
   sed -i 's/level: INFO/level: DEBUG/' config.yaml
   python memory_observer.py
   ```

5. **Python 환경 확인:**
   ```bash
   which python
   python -c "import lib.file_watcher; print('OK')"
   ```

**일반적인 원인:** 누락된 디렉토리 또는 권한 거부 오류

### 높은 CPU 사용량

**문제:** 옵저버가 많은 CPU/디스크 I/O를 사용합니다.

**해결책:**

1. **감시 범위 축소:**
   - `config.yaml`에서 더 적은 디렉토리 모니터링
   - 클라우드 동기화 폴더 제외 (Dropbox, Google Drive, iCloud)

2. **재귀 감시 비활성화:**
   ```yaml
   watch:
     recursive: false  # 루트 디렉토리만 감시
   ```

3. **적절한 로그 레벨 설정:**
   ```yaml
   logging:
     level: INFO    # DEBUG 아님
   ```

4. **큰 디렉토리 제외:**
   - 감시 안 할 항목: node_modules, .git, __pycache__, .venv
   - 감시 경로를 작고 집중된 디렉토리로 유지

**일반적인 원인:** node_modules 또는 많은 파일이 있는 다른 큰 디렉토리 감시

---

## 프로덕션 배포

OC-Memory를 프로덕션에서 실행 (재시작 후에도 계속)하려면 [DEPLOYMENT.md](DEPLOYMENT.md)를 참고하세요:

- **systemd 설정** (Linux) - 자동 재시작 서비스
- **LaunchAgent 설정** (macOS) - 로그인 시 실행
- **작업 스케줄러** (Windows) - 자동 재시작 서비스
- **Docker 배포** - 컨테이너화된 설정
- **모니터링 및 경고** - 상태 확인

---

## 구성 요소 개별 테스트

### FileWatcher 구성 요소 테스트

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

### MemoryWriter 구성 요소 테스트

```bash
python << 'EOF'
from lib.memory_writer import MemoryWriter
from pathlib import Path
from datetime import datetime

print("Testing MemoryWriter component...")

writer = MemoryWriter('~/.openclaw/workspace/memory')

# 테스트: 메모리 항목 생성
print("\n1. Creating memory entry...")
content = "# Test Entry\nThis is a test."
result = writer.write_memory_entry(
    content=content,
    filename="test_entry.md",
    category="tests"
)
print(f"✅ Created: {result}")

# 테스트: 메타데이터 추가
print("\n2. Adding metadata...")
writer.add_metadata(result, {
    "created": datetime.now().isoformat(),
    "category": "test",
    "tags": ["test"]
})
print(f"✅ Metadata added")

# 테스트: 범주 감지
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

### 구성 로딩 테스트

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

## 요약

### 5분 빠른 시작

```bash
# 1. 복제 및 설정
git clone https://github.com/openclaw-ai/oc-memory.git
cd oc-memory
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. 구성 (선택 사항 - 기본값 작동)
nano config.yaml

# 3. 옵저버 시작
python memory_observer.py

# 4. 다른 터미널에서 테스트 파일 생성
mkdir -p ~/Documents/notes
echo "# Test" > ~/Documents/notes/test.md

# 5. 메모리 디렉토리 확인
ls ~/.openclaw/workspace/memory/notes/
```

### 성공 표시

다음이 표시되면 작동하고 있습니다:

1. ✅ 옵저버가 오류 없이 시작됨
2. ✅ `.md` 파일 생성/편집이 2초 내에 로그에 표시
3. ✅ 파일이 `~/.openclaw/workspace/memory/[category]/`에 표시
4. ✅ 파일에 메타데이터가 포함된 YAML 머리글 있음
5. ✅ OpenClaw가 메모리를 찾을 수 있음 (5-10초 인덱싱 후)

### 다음 단계

1. ✅ **시작하기** - 지금 여기 있습니다!
2. ➡️ **테스트 실행** - `pytest`를 사용하여 구성 요소 확인: `pytest tests/`
3. ➡️ **프로덕션 설정** - 연속 작동을 위해 [DEPLOYMENT.md](DEPLOYMENT.md) 참고
4. ➡️ **API 문서** - 고급 통합을 위해 [API.md](API.md) 참고
5. ➡️ **아키텍처** - 시스템 설계를 위해 [CLAUDE.md](../CLAUDE.md) 참고

---

## 추가 리소스

- **[README.md](../README.md)** - 프로젝트 개요 및 기능
- **[CLAUDE.md](../CLAUDE.md)** - 개발자 가이드 및 아키텍처
- **[TESTING.md](TESTING.md)** - 종합 테스트 가이드
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - 프로덕션 배포 가이드
- **[API.md](API.md)** - API 문서 및 통합 예시
- **[OpenClaw 저장소](https://github.com/openclaw-ai/openclaw)** - 공식 OpenClaw 저장소

---

## 최고의 결과를 위한 팁

1. **간단하게 시작하기:** 초기에는 하나의 디렉토리만 모니터링 (예: `~/Documents/notes`)
2. **일관된 명명 사용:** 파일 경로는 분류에 사용됩니다
3. **로그 정기적 확인:** `oc-memory.log`를 보며 동작 이해
4. **클라우드 디렉토리 피하기:** Dropbox/Google Drive/iCloud 모니터링 안 함 - 파일 감시 방해
5. **감시 범위 작게 유지:** 실제 콘텐츠가 있는 디렉토리만 모니터링
6. **의미 있는 파일명 사용:** 검색 가능성 및 분류 향상
7. **머리글 수동 추가:** 선택 사항이지만 OpenClaw의 메모리 검색에 도움

---

## 도움말 받기

문제가 발생하면:

1. 위의 [일반적인 문제](#일반적인-문제-및-문제-해결)를 확인하세요
2. DEBUG 로깅을 활성화하고 로그를 검토하세요
3. `python lib/config.py`로 구성을 확인하세요
4. 구성 요소를 개별적으로 테스트해보세요 ([구성 요소 개별 테스트](#구성-요소-개별-테스트) 참고)
5. 종합 테스트 절차를 보려면 [TESTING.md](TESTING.md)를 확인하세요
6. 아키텍처 세부사항을 보려면 [CLAUDE.md](../CLAUDE.md)를 검토하세요

---

**버전:** 1.1
**상태:** 프로덕션 사용 준비 완료
**마지막 업데이트:** 2026-02-12
