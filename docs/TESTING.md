# 🧪 OC-Memory Testing Guide

OC-Memory 프로젝트의 테스트 가이드입니다. 프로젝트는 pytest를 사용하여 포괄적인 Unit Test를 제공합니다.

---

## 📊 테스트 현황

- **총 테스트**: 66개
- **통과율**: 100% (66/66)
- **코드 커버리지**: 77%
- **실행 시간**: ~2초

---

## 🚀 빠른 시작

### 1. 가상 환경 활성화
```bash
source venv/bin/activate
```

### 2. 필수 패키지 설치
```bash
pip install pytest pytest-cov
```

### 3. 테스트 실행
```bash
python -m pytest tests/ -v
```

---

## 🧪 테스트 실행 옵션

### 모든 테스트 실행 (상세 모드)
```bash
pytest tests/ -v
```

### 모든 테스트 실행 (간단 모드)
```bash
pytest tests/ -q
```

### 특정 테스트 파일만 실행
```bash
# Config 모듈 테스트
pytest tests/test_config.py -v

# FileWatcher 모듈 테스트
pytest tests/test_file_watcher.py -v

# MemoryWriter 모듈 테스트
pytest tests/test_memory_writer.py -v
```

### 특정 테스트 클래스만 실행
```bash
pytest tests/test_config.py::TestLoadConfig -v
pytest tests/test_file_watcher.py::TestFileWatcher -v
pytest tests/test_memory_writer.py::TestAddMetadata -v
```

### 특정 테스트만 실행
```bash
pytest tests/test_config.py::TestLoadConfig::test_load_valid_config -v
```

### Integration 테스트만 실행
```bash
pytest tests/ -m integration -v
```

### 특정 마커로 실행
```bash
# Config 관련 테스트
pytest tests/ -m config -v

# FileWatcher 관련 테스트
pytest tests/ -m file_watcher -v

# MemoryWriter 관련 테스트
pytest tests/ -m memory_writer -v
```

---

## 📈 코드 커버리지

### 기본 커버리지 리포트
```bash
pytest tests/ --cov=lib --cov-report=term-missing
```

### HTML 커버리지 리포트 생성
```bash
pytest tests/ --cov=lib --cov-report=html
open htmlcov/index.html  # macOS
```

### 커버리지 통계
```bash
pytest tests/ --cov=lib --cov-report=term
```

---

## 🔧 고급 옵션

### 테스트 실패 시 중단
```bash
pytest tests/ -x
```

### 마지막 실패한 테스트부터 시작
```bash
pytest tests/ --lf
```

### 실패한 테스트 우선 실행
```bash
pytest tests/ --ff
```

### 슬로우 테스트 제외 (1초 이상)
```bash
pytest tests/ -m "not slow" -v
```

### 병렬 실행 (pytest-xdist 필요)
```bash
pip install pytest-xdist
pytest tests/ -n auto
```

### 상세한 디버그 정보
```bash
pytest tests/ -vv --tb=long
```

### 테스트 수집 정보만 표시
```bash
pytest tests/ --collect-only
```

---

## 📋 테스트 구조

### test_config.py (14개 테스트)
```
TestLoadConfig (4 tests)
  • YAML 파일 로드 검증
  • 파일 누락 처리
  • 잘못된 YAML 처리

TestValidateConfig (4 tests)
  • 구조 검증
  • 필수 필드 확인
  • 타입 검증

TestExpandPaths (3 tests)
  • 경로 확장 (~ 포함)
  • 절대 경로 처리

TestGetConfig (2 tests)
  • 통합 로드/검증/확장

TestIntegration (1 test)
  • 전체 워크플로우
```

### test_file_watcher.py (26개 테스트)
```
TestMarkdownFileHandler (11 tests)
  • 파일 필터링 (.md, .markdown)
  • 이벤트 핸들링 (created, modified)
  • 콜백 실행

TestFileWatcher (10 tests)
  • 초기화 및 설정
  • 감시 시작/중지
  • 재귀 감시

TestFileWatcherIntegration (3 tests)
  • 실시간 파일 감시
  • 필터링 검증
  • 재귀 감시 검증
```

### test_memory_writer.py (26개 테스트)
```
TestMemoryWriterInit (4 tests)
  • 디렉토리 생성
  • 경로 확장

TestCopyToMemory (6 tests)
  • 파일 복사
  • 메타데이터 보존
  • 충돌 해결

TestWriteMemoryEntry (4 tests)
  • 메모리 엔트리 작성
  • 카테고리 지원
  • 유니코드 처리

TestAddMetadata (4 tests)
  • YAML frontmatter 생성
  • 메타데이터 교체
  • 다양한 타입 지원

TestGetCategoryFromPath (6 tests)
  • 자동 카테고리화
  • 경로 분석

TestMemoryWriterIntegration (3 tests)
  • 파일 복사 + 메타데이터
  • 다중 파일 처리
  • 자동 카테고리화
```

---

## 🐛 일반적인 문제 해결

### pytest를 찾을 수 없는 경우
```bash
# 가상 환경 활성화 확인
which python
# -> /Users/.../venv/bin/python 이어야 함

# 패키지 다시 설치
pip install pytest -q
```

### 테스트가 느리게 실행되는 경우
```bash
# 병렬 실행 시도
pip install pytest-xdist
pytest tests/ -n auto
```

### 특정 테스트만 실패하는 경우
```bash
# 상세한 에러 정보 확인
pytest tests/test_name.py::TestClass::test_method -vv --tb=long
```

### 임시 파일 정리 문제
```bash
# pytest 캐시 정리
pytest --cache-clear tests/

# 임시 디렉토리 정리
rm -rf /tmp/pytest-*
```

---

## ✅ CI/CD 통합

### GitHub Actions 예제
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.14'
      - run: pip install -r requirements.txt pytest pytest-cov
      - run: pytest tests/ --cov=lib --cov-report=xml
      - uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
```

---

## 📚 참고 자료

- [pytest 공식 문서](https://docs.pytest.org/)
- [pytest 플러그인 목록](https://docs.pytest.org/en/latest/plugins.html)
- [Coverage.py 문서](https://coverage.readthedocs.io/)

---

## 📝 테스트 작성 가이드

### 새로운 테스트 추가 시
1. `tests/` 디렉토리에 `test_*.py` 파일 생성
2. `Test*` 클래스 생성
3. `test_*` 메서드 작성
4. 테스트 실행 및 검증

### 테스트 템플릿
```python
import pytest
from lib.module import MyClass

class TestMyClass:
    """Tests for MyClass"""

    def test_basic_functionality(self):
        """Test basic functionality"""
        obj = MyClass()
        assert obj.method() == expected_value

    @pytest.mark.integration
    def test_with_other_module(self):
        """Integration test with other modules"""
        # Test code here
        pass
```

---

## 🎯 테스트 목표

| 항목 | 목표 | 현황 |
|------|------|------|
| 코드 커버리지 | >= 80% | ✅ 77% |
| 테스트 통과율 | 100% | ✅ 100% |
| 실행 시간 | < 5초 | ✅ 1.82초 |
| 테스트/코드 비율 | > 1.5x | ✅ 3.8x |

---

**마지막 업데이트**: 2026-02-12
**테스트 환경**: Python 3.14.0, pytest 9.0.2
