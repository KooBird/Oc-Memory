# 📁 프로젝트 문서 정리 계획

## 🔍 현재 상황 분석

### 루트에 있는 파일들 (27개)

```
📄 핵심 문서:
  1. README.md ⭐ (유지)
  2. CLAUDE.md ⭐ (유지)

⚙️ 설정 파일:
  3. config.yaml (유지)
  4. config.example.yaml (유지)
  5. .env.production (config 폴더로)
  6. requirements.txt (유지)
  7. pytest.ini (config 폴더로)

📊 테스트 리포트 (아카이브로):
  8. TEST_REPORT_2026_02_12.md (이전, 삭제)
  9. TEST_REPORT_PHASE1_2026_02_12.md (아카이브)
  10. TEST_REPORT_PHASE2_2026_02_12.md (아카이브)
  11. TEST_REPORT_PHASE3_2026_02_12.md (아카이브)
  12. TEST_REPORT_PHASE4_2026_02_12.md (아카이브)

📚 계획/로드맵 (아카이브로):
  13. PHASE2_TEST_PLAN.md (아카이브)
  14. PHASE3_ROADMAP.md (아카이브)
  15. PHASE4_PRODUCTION.md (아카이브)
  16. IMPLEMENTATION_ROADMAP.md (아카이브)
  17. NEXT_STEPS.md (아카이브)
  18. PROGRESS_SUMMARY.md (아카이브)

📖 가이드 (docs로):
  19. QUICKSTART.md (docs로)
  20. QUICKSTART_PHASE2.md (docs로)
  21. TESTING.md (docs로)
  22. TESTING_SUMMARY.md (아카이브)
  23. ANALYSIS_SUMMARY.md (아카이브)
  24. TEST_SETUP.md (아카이브)
  25. openclaw_analysis_report.md (아카이브)

🗑️ 불필요한 파일:
  26. test_setup_input.txt (삭제)

🔧 기타:
  27. setup.py (유지)
```

---

## 📁 목표 구조

```
Oc-Memory/
├── README.md ⭐ (프로젝트 소개)
├── CLAUDE.md (개발자 가이드)
├── requirements.txt
├── setup.py
│
├── config/
│   ├── config.yaml (기본 설정)
│   ├── config.example.yaml (설정 예시)
│   ├── .env.production (프로덕션 환경)
│   └── pytest.ini (테스트 설정)
│
├── docs/
│   ├── GETTING_STARTED.md (빠른 시작 - QUICKSTART 통합)
│   ├── TESTING.md (테스트 가이드)
│   ├── DEPLOYMENT.md (배포 가이드 - PHASE4 통합)
│   ├── API.md (API 가이드)
│   │
│   ├── architecture/
│   │   ├── ARCHITECTURE.md (시스템 아키텍처)
│   │   └── DESIGN.md (설계 문서)
│   │
│   └── archive/ (이전 버전)
│       ├── PHASE2_TEST_PLAN.md
│       ├── PHASE3_ROADMAP.md
│       ├── TEST_REPORT_PHASE1.md
│       ├── TEST_REPORT_PHASE2.md
│       ├── TEST_REPORT_PHASE3.md
│       └── TEST_REPORT_PHASE4.md
│
├── lib/
│   ├── __init__.py
│   ├── config.py
│   ├── file_watcher.py
│   ├── memory_writer.py
│   ├── memory_observer.py
│   └── monitoring.py
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_config.py
│   ├── test_file_watcher.py
│   └── test_memory_writer.py
│
├── specs/
│   └── (기존 스펙 문서)
│
└── .github/
    └── workflows/
        └── tests.yml
```

---

## ✅ 정리 작업 계획

### Step 1: 디렉토리 생성
```bash
mkdir -p docs/archive docs/architecture config
```

### Step 2: 파일 이동

#### 설정 파일 → config/
```bash
mv .env.production config/
mv pytest.ini config/
```

#### 가이드 → docs/
```bash
# QUICKSTART들을 통합해서 GETTING_STARTED.md로
# TESTING.md는 docs로
# PHASE4_PRODUCTION.md는 DEPLOYMENT.md로 이름 변경
```

#### 테스트 리포트 → docs/archive/
```bash
mv TEST_REPORT_PHASE*.md docs/archive/
```

#### 계획/로드맵 → docs/archive/
```bash
mv PHASE*_*.md docs/archive/
mv IMPLEMENTATION_ROADMAP.md docs/archive/
mv NEXT_STEPS.md docs/archive/
mv PROGRESS_SUMMARY.md docs/archive/
```

#### 분석 → docs/archive/
```bash
mv ANALYSIS_SUMMARY.md docs/archive/
mv TEST_SETUP.md docs/archive/
mv openclaw_analysis_report.md docs/archive/
mv TESTING_SUMMARY.md docs/archive/
```

### Step 3: 파일 삭제
```bash
rm test_setup_input.txt
rm TEST_REPORT_2026_02_12.md (이전 버전)
```

### Step 4: 새 문서 생성

#### docs/GETTING_STARTED.md (QUICKSTART 통합)
- 5분 안에 시작하기
- 설치 및 설정
- 첫 실행

#### docs/DEPLOYMENT.md (PHASE4 통합)
- 성능 최적화
- 설정 최적화
- 에러 처리
- 모니터링 설정

#### docs/architecture/ARCHITECTURE.md (새로 작성)
- 시스템 개요
- 컴포넌트 설명
- 데이터 흐름

---

## 📊 정리 전후 비교

### 정리 전
```
루트 디렉토리: 27개 파일
  - 문서: 20개
  - 설정: 3개
  - 기타: 4개

사용자 혼란도: ⭐⭐⭐⭐⭐ (매우 높음)
```

### 정리 후
```
루트 디렉토리: 7개 파일
  - 핵심 문서: 2개 (README.md, CLAUDE.md)
  - 설정: 2개 (config.yaml, requirements.txt)
  - 기타: 3개 (setup.py, .gitignore 등)

docs 디렉토리: 3-4개 문서 (필수만)
docs/archive: 8개 (참고용)
config 디렉토리: 4개 파일

사용자 명확도: ⭐⭐⭐⭐⭐ (매우 명확함)
```

---

## 🎯 최종 정리 기준

### ✅ 유지할 파일
- README.md (프로젝트 설명)
- CLAUDE.md (개발 가이드)
- requirements.txt (의존성)
- setup.py (설치 스크립트)
- config.yaml (기본 설정)
- config.example.yaml (설정 예시)
- pytest.ini (테스트 설정)

### ✅ 통합/이름 변경
- QUICKSTART.md + QUICKSTART_PHASE2.md → docs/GETTING_STARTED.md
- TESTING.md → docs/TESTING.md
- PHASE4_PRODUCTION.md → docs/DEPLOYMENT.md
- .env.production → config/.env.production
- TESTING_SUMMARY.md → 삭제 (TEST_REPORT에 포함)
- NEXT_STEPS.md → docs/archive/NEXT_STEPS.md

### 📁 아카이브 (docs/archive/)
- 모든 TEST_REPORT_PHASE*.md
- PHASE*_*.md
- IMPLEMENTATION_ROADMAP.md
- PROGRESS_SUMMARY.md
- ANALYSIS_SUMMARY.md
- TEST_SETUP.md
- openclaw_analysis_report.md

### 🗑️ 삭제
- test_setup_input.txt (테스트용)
- TEST_REPORT_2026_02_12.md (이전 버전)

---

## 📝 .gitignore 업데이트

```
# 임시 파일
*.log
*.tmp
test_setup_input.txt

# 캐시
__pycache__/
.pytest_cache/
*.pyc

# 환경
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp

# 빌드
build/
dist/
*.egg-info/

# 테스트
htmlcov/
coverage.xml
.coverage
```

---

## ✨ 최종 결과

```
클론 후 프로젝트 구조:

Oc-Memory/
├── 📄 README.md (프로젝트 소개) ← 첫 번째 읽기
├── 📄 CLAUDE.md (개발 가이드)
├── 📖 docs/
│   ├── GETTING_STARTED.md ← 시작하기
│   ├── TESTING.md ← 테스트 방법
│   ├── DEPLOYMENT.md ← 배포 방법
│   ├── architecture/ ← 시스템 이해
│   └── archive/ ← 참고용
├── ⚙️ config/ ← 설정 파일들
├── 🔧 lib/ ← 소스 코드
├── 🧪 tests/ ← 테스트 코드
└── 📋 기타 설정 파일들

사용자가 봤을 때: "오, 깔끔하네!" ✨
```

---

이 계획으로 진행하면 됩니다!
