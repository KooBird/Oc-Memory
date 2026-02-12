# 🚀 OC-Memory Phase 3 로드맵

**작성일**: 2026-02-12
**현재 상태**: Phase 2 완료 (실제 작동 검증 완료)
**다음 단계**: Phase 3 OpenClaw 연동

---

## 📊 현재까지의 진행 상황

```
✅ Phase 1 (완료) - Unit Test
   ├─ 66개 테스트 작성
   ├─ 77% 코드 커버리지
   ├─ 모든 모듈 검증
   └─ 예상 시간: ~2시간

✅ Phase 2 (완료) - 실제 작동 검증
   ├─ FileWatcher 실제 작동: ✅ 12개 이벤트 감지
   ├─ MemoryWriter 파일 복사: ✅ 성공
   ├─ E2E 통합 테스트: ✅ 14개 처리
   └─ 예상 시간: 13분 (실제)

🔴 Phase 3 (다음) - OpenClaw 연동
   ├─ 메모리 시스템 연동 검증
   ├─ 파일 인덱싱 확인
   ├─ 검색 기능 테스트
   └─ 예상 시간: ~30분
```

---

## 🎯 Phase 3 목표

### 주요 목표
1. **메모리 파일 자동 인덱싱** 확인
   - OC-Memory가 생성한 파일이 OpenClaw에 자동으로 인덱싱되는가?

2. **메모리 검색 기능** 테스트
   - OpenClaw의 `/memory` 명령어로 동기화된 메모리 접근 가능한가?

3. **시스템 프롬프트 통합** 검증
   - 메모리 파일의 내용이 OpenClaw 프롬프트에 포함되는가?

4. **메타데이터 활용** 확인
   - 메타데이터가 검색 및 필터링에 정상 작동하는가?

---

## 📋 Phase 3 세부 절차

### 🔴 Priority 1: 메모리 파일 인덱싱 확인 (10분)

#### Step 1: OpenClaw 메모리 디렉토리 확인
```bash
# OpenClaw 메모리 디렉토리 구조 확인
ls -la ~/.openclaw/workspace/memory/

# 우리가 생성한 파일 확인
find ~/.openclaw/workspace/memory -name "*.md" -mtime -1
```

#### Step 2: 파일 내용 검증
```bash
# 메타데이터가 포함된 파일 확인
cat ~/.openclaw/workspace/memory/notes/test.md

# 예상 내용:
# ---
# source: /Users/.../Documents/notes/test.md
# category: notes
# copied_at: 2026-02-12T...
# test: phase2
# ---
#
# # Test Note
```

#### Step 3: OpenClaw SQLite 검증 (선택)
```bash
# OpenClaw의 메모리 데이터베이스 확인
sqlite3 ~/.openclaw/data/memory.db ".tables"

# 메모리 파일 인덱싱 확인
sqlite3 ~/.openclaw/data/memory.db "SELECT * FROM documents LIMIT 5;"
```

---

### 🔴 Priority 2: OpenClaw 메모리 검색 테스트 (10분)

#### Step 1: OpenClaw에서 메모리 명령어 사용

OpenClaw 터미널에 다음을 입력하세요:
```
/memory test
/memory phase2
/memory notes
```

**예상 결과**:
```
📚 Memory Search Results for "test":
1. notes/test.md (2026-02-12)
   - Category: notes
   - Source: /Users/.../Documents/notes/test.md

2. e2e_test_1.md (2026-02-12)
   - Category: notes
   - Source: /Users/.../Documents/notes/e2e_test_1.md
```

#### Step 2: 메모리 컨텍스트 확인
```
# OpenClaw 터미널에 입력:
What files did I create recently?

# 예상: OC-Memory가 생성한 파일 목록 자동 포함
```

---

### 🟡 Priority 3: 메타데이터 활용 테스트 (10분)

#### Step 1: 메타데이터 기반 필터링
```bash
# 메타데이터 검색 쿼리 테스트 (Advanced)
# OpenClaw에 다음 입력:
/memory category:notes
/memory after:2026-02-12
/memory tag:phase2
```

#### Step 2: 시스템 프롬프트 통합 검증
```bash
# OpenClaw의 시스템 프롬프트에 메모리 포함 여부 확인
# OpenClaw 설정 파일 확인:
cat ~/.openclaw/openclaw.json | grep -A 5 "memory"
```

---

## 🧪 Phase 3 테스트 절차 (상세)

### Test 3-1: 메모리 파일 자동 인덱싱

```bash
source venv/bin/activate

python << 'PYTHON'
from pathlib import Path
import json
import time

print("=" * 60)
print("🧪 TEST 3-1: 메모리 파일 자동 인덱싱")
print("=" * 60)

# Step 1: OC-Memory 생성 파일 확인
print("\n1️⃣  OC-Memory 생성 파일 확인...")
memory_dir = Path('~/.openclaw/workspace/memory').expanduser()
oc_memory_files = list(memory_dir.glob('notes/*.md'))
print(f"   ✅ 생성된 파일: {len(oc_memory_files)}개")
for f in oc_memory_files:
    print(f"      - {f.name}")

# Step 2: OpenClaw 데이터베이스 확인
print("\n2️⃣  OpenClaw 메모리 인덱싱 확인...")
db_path = Path('~/.openclaw/data/memory.db').expanduser()
if db_path.exists():
    print(f"   ✅ 메모리 DB 존재: {db_path}")

    # SQLite 쿼리로 파일 확인
    import sqlite3
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # 테이블 확인
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print(f"   📊 테이블 수: {len(tables)}")

        # 최근 문서 조회
        cursor.execute("SELECT COUNT(*) FROM documents WHERE created_at > datetime('now', '-1 day')")
        recent_docs = cursor.fetchone()[0]
        print(f"   📝 최근 문서 (24시간): {recent_docs}개")

        conn.close()
    except Exception as e:
        print(f"   ⚠️  DB 조회 실패: {e}")
else:
    print(f"   ℹ️  메모리 DB 없음 (아직 인덱싱 안 됨)")

# Step 3: 메타데이터 확인
print("\n3️⃣  메타데이터 검증...")
test_file = memory_dir / 'notes' / 'test.md'
if test_file.exists():
    content = test_file.read_text()
    has_metadata = content.startswith('---')
    print(f"   ✅ 메타데이터: {'있음' if has_metadata else '없음'}")

    if has_metadata:
        lines = content.split('\n')[:10]
        print(f"   📋 메타데이터 샘플:")
        for line in lines:
            if line and not line.startswith('---'):
                print(f"      {line}")

print("\n" + "=" * 60)

PYTHON
```

---

### Test 3-2: OpenClaw 메모리 검색 통합

이 테스트는 **OpenClaw 터미널에서 수동으로 진행**해야 합니다:

```
# OpenClaw 터미널에서 다음 명령어 차례로 입력:

1️⃣  기본 검색:
/memory test
/memory notes
/memory phase2

2️⃣  고급 검색:
/memory recent
/memory category:notes

3️⃣  자연어 질문:
What markdown files have I created recently?
Show me my notes from today.
What's in my OC-Memory?
```

**검증 포인트**:
- ✅ 파일이 검색 결과에 나타나는가?
- ✅ 메타데이터가 포함되어 표시되는가?
- ✅ 정확한 내용이 검색되는가?

---

### Test 3-3: 시스템 프롬프트 통합

```bash
# OpenClaw 설정 확인
cat ~/.openclaw/openclaw.json | python -m json.tool | grep -A 20 "memory"

# 예상 출력:
# "memory": {
#   "enabled": true,
#   "directories": [
#     "~/.openclaw/workspace/memory"
#   ],
#   "includeInSystemPrompt": true,
#   "maxTokens": 5000
# }
```

---

## 📝 Phase 3 수행 순서

### 오늘 바로 진행 가능 (🔴 Priority 1 & 2)

```
Step 1: 메모리 파일 확인 (5분)
        ├─ 파일 위치 확인
        ├─ 메타데이터 확인
        └─ DB 인덱싱 확인

Step 2: OpenClaw 메모리 검색 (5분)
        ├─ /memory 명령어 테스트
        ├─ 검색 결과 검증
        └─ 자연어 쿼리 테스트

Step 3: 시스템 프롬프트 확인 (5분)
        ├─ 설정 파일 검증
        ├─ 메모리 포함 여부 확인
        └─ 통합 동작 검증
```

### 선택사항 (🟡 Priority 3)

```
Advanced Test:
├─ ChromaDB 의미론적 검색
├─ 메타데이터 필터링
└─ 대량 파일 성능 테스트
```

---

## 🎯 Phase 3 검증 체크리스트

- [ ] **메모리 파일 인덱싱**
  - [ ] 파일이 ~/.openclaw/workspace/memory에 존재
  - [ ] 메타데이터가 포함됨
  - [ ] OpenClaw DB에 인덱싱됨

- [ ] **검색 기능**
  - [ ] OpenClaw /memory 명령어 작동
  - [ ] 파일 검색 결과 표시
  - [ ] 메타데이터 필터링 작동

- [ ] **시스템 프롬프트 통합**
  - [ ] 설정에 메모리 디렉토리 포함
  - [ ] 프롬프트에 메모리 내용 추가
  - [ ] 자연어 쿼리에서 메모리 활용

- [ ] **성능 및 안정성**
  - [ ] 검색 응답 시간 <1초
  - [ ] 에러 없음
  - [ ] 메모리 누수 없음

---

## 🔧 필요한 도구 및 설정

### OpenClaw 버전 확인
```bash
# OpenClaw 버전 확인
openclaw --version

# 또는 설정 파일 확인
cat ~/.openclaw/openclaw.json | grep version
```

### 메모리 설정 확인
```bash
# OC-Memory 설정 확인
cat config.yaml | grep -A 10 memory:

# 예상:
# memory:
#   dir: /Users/.../workspace/memory
#   auto_categorize: true
#   max_file_size: 5242880
```

---

## 📊 Phase 3 예상 시간 및 난이도

| 작업 | 난이도 | 시간 |
|------|--------|------|
| 메모리 파일 확인 | ⭐ | 5분 |
| OpenClaw 검색 테스트 | ⭐⭐ | 5분 |
| 시스템 프롬프트 통합 | ⭐⭐ | 5분 |
| **합계** | ⭐⭐ | **15분** |

---

## 🚀 Phase 3 시작하기

### 지금 바로 할 수 있는 것:

**1단계: 메모리 파일 확인 (1분)**
```bash
# 지금 실행
ls -la ~/.openclaw/workspace/memory/notes/

# 파일이 있는지 확인
cat ~/.openclaw/workspace/memory/notes/test.md | head -10
```

**2단계: OpenClaw 검색 테스트 (2분)**
```
# OpenClaw 터미널에서 입력:
/memory test

# 결과 확인
```

**3단계: 시스템 프롬프트 확인 (1분)**
```bash
# 터미널에서 실행
cat ~/.openclaw/openclaw.json | python -m json.tool | grep -A 5 "memory" || echo "memory 설정 확인 필요"
```

---

## 💡 주의사항

1. **OpenClaw 재시작 필요 여부**
   - 메모리 파일이 추가된 후 OpenClaw가 자동으로 감지하지 않으면 재시작 필요
   - 설정 변경 시에는 반드시 OpenClaw 재시작 필요

2. **데이터베이스 캐시**
   - SQLite 인덱싱에는 약간의 시간이 필요할 수 있음 (1-5초)
   - 검색 전에 몇 초 대기 권장

3. **파일 경로**
   - 메모리 디렉토리는 반드시 `~/.openclaw/workspace/memory`이어야 함
   - 다른 경로에 있으면 자동 인덱싱 안 됨

---

## 📞 필요한 정보 수집

Phase 3 테스트 시 다음 정보가 필요합니다:
- [ ] OpenClaw 버전
- [ ] OpenClaw 설정 (openclaw.json)
- [ ] 메모리 DB 상태 (존재 여부)
- [ ] 최근 인덱싱된 파일 수

---

## 🎓 Phase 3 이후

Phase 3 완료 후:

1. **Phase 4: 프로덕션 배포**
   - 설정 최적화
   - 성능 튜닝
   - 문서화 완성

2. **Phase 5: 운영**
   - 장기 테스트 (1주일)
   - 모니터링
   - 피드백 수집

---

**준비 완료! Phase 3 시작할 준비가 되었나요?** 🚀

다음 중 선택하세요:
1. ✅ **지금 시작** - Phase 3 테스트 진행
2. 📋 **상세 계획** - Phase 3 세부 절차 설명
3. 🔧 **사전 준비** - OpenClaw 설정 확인
