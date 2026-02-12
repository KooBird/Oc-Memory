# OC-Memory: OpenClaw 외장형 기억 시스템

**OpenClaw에 90일 이상의 장기 기억 능력을 부여하는 독립형 메모리 시스템**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Status: Production Ready](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)]()

---

## 🎯 이게 뭐예요?

OC-Memory는 **OpenClaw AI에 외부 기억 능력을 추가**하는 시스템입니다.

### 간단히 말하면
- **대화 기록 저장**: 마크다운 파일로 자동 저장
- **90일 이상 보관**: 오래된 기억도 찾아 사용 가능
- **OpenClaw 기본 수정 없음**: 완전 독립형 시스템
- **비용 절감**: 토큰 사용 90% 감소

### 실제 효과
```
이전: "어제 뭐했는지 안 기억나... 다시 말해줄래?"
↓
이후: "어제 우리 대화 읽고 바로 답변할게!"
```

---

## ⚡ 5분 안에 시작하기

### 1단계: 설치 (2분)

```bash
# 리포지토리 클론
git clone https://github.com/chaos1358/Oc-Memory.git
cd Oc-Memory

# Python 패키지 설치
pip install -r requirements.txt
```

**예상 결과**: 특별한 에러 없이 설치 완료

### 2단계: 설정 (2분)

```bash
# 설정 파일 복사
cp config/config.example.yaml config/config.yaml

# 설정 파일 수정 (에디터로 열기)
# 주의: 다음 항목만 수정하면 됨
# - watch.dirs: 감시할 폴더 경로
# - memory.dir: 메모리 저장 폴더 (기본값 OK)
```

### 3단계: 실행 (1분)

```bash
# 메모리 관찰자 시작
python memory_observer.py
```

**예상 결과**:
```
============================================================
Starting OC-Memory Observer
============================================================
Watch directories: ['/Users/your-name/Documents/notes', ...]
Memory directory: /Users/your-name/.openclaw/workspace/memory
============================================================
OC-Memory Observer started successfully
Monitoring for file changes... (Press Ctrl+C to stop)
```

### 4단계: 테스트 (✅ 성공 확인)

**다른 터미널에서 실행**:
```bash
# 테스트 파일 생성
mkdir -p ~/Documents/notes
echo "# Test Note" > ~/Documents/notes/test.md
```

**원래 터미널에서 확인**:
```bash
# 파일이 감지되었는지 확인
# 메모리 폴더에 저장되었는지 확인

ls ~/.openclaw/workspace/memory/notes/
```

**성공 기준**: 파일이 자동으로 생성되고 메타데이터가 추가됨

---

## 📖 다음 단계

### 초보자
👉 **[GETTING_STARTED.md](./docs/GETTING_STARTED.md)**
- 상세 설치 가이드
- 각 기능별 테스트 방법
- 문제 해결

### 개발자
👉 **[CLAUDE.md](./CLAUDE.md)**
- 프로젝트 아키텍처
- 코드 구조
- 개발 환경 설정

### 테스트
👉 **[docs/TESTING.md](./docs/TESTING.md)**
- 단위 테스트 (66개)
- 통합 테스트
- 성능 테스트

### 프로덕션 배포
👉 **[docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md)**
- 성능 최적화 (1000+ files/sec)
- 모니터링 설정
- systemd/LaunchAgent 배포

---

## 🏗️ 시스템 구조

```
OC-Memory (외부 프로세스)
    ↓
📂 파일 감시 (FileWatcher)
    ├─ ~/Documents/notes 모니터링
    ├─ 마크다운 파일 자동 감지
    └─ 변경 사항 실시간 추적
    ↓
📝 메모리 저장 (MemoryWriter)
    ├─ 파일 자동 복사
    ├─ 메타데이터 추가 (날짜, 카테고리)
    └─ OpenClaw 메모리 폴더에 저장
    ↓
🧠 OpenClaw가 자동 사용
    ├─ 대화할 때 기억 참고
    ├─ 컨텍스트 자동 로드
    └─ 일관된 대화 유지
```

---

## ✅ 현재 상태

| 기능 | 상태 |
|------|------|
| **핵심 메모리 시스템** | ✅ 완성 |
| **파일 감시 기능** | ✅ 완성 |
| **자동 분류** | ✅ 완성 |
| **메타데이터** | ✅ 완성 |
| **단위 테스트** | ✅ 66개 통과 |
| **통합 테스트** | ✅ 모두 통과 |
| **성능 최적화** | ✅ 1374 files/sec |
| **CI/CD 자동화** | ✅ GitHub Actions |
| **프로덕션 준비** | ✅ 완료 |

**상태**: 🟢 **프로덕션 배포 준비 완료**

---

## 🛠️ 기술 스택

| 구성 | 기술 |
|------|------|
| **언어** | Python 3.10+ |
| **의존성 추적** | watchdog (파일 감시) |
| **저장소** | Markdown 파일 + YAML 메타데이터 |
| **성능** | 1374 files/sec, 0.31MB 메모리 사용 |
| **배포** | systemd (Linux), LaunchAgent (macOS) |

---

## 📚 상세 문서

### 빠른 참고
- **[GETTING_STARTED.md](./docs/GETTING_STARTED.md)** - 설치 및 기본 사용법
- **[TESTING.md](./docs/TESTING.md)** - 테스트 절차
- **[DEPLOYMENT.md](./docs/DEPLOYMENT.md)** - 프로덕션 배포

### 개발 문서
- **[CLAUDE.md](./CLAUDE.md)** - 개발자 가이드
- **[specs/BRD.md](./specs/BRD.md)** - 비즈니스 요구사항
- **[specs/PRD.md](./specs/PRD.md)** - 제품 명세
- **[specs/Tech_Spec.md](./specs/Tech_Spec.md)** - 기술 설계

### 참고 문서
- **[docs/archive/](./docs/archive/)** - Phase별 테스트 리포트, 로드맵

---

## 🚀 자주 묻는 질문

### Q: 설치 중에 에러가 나요
A: [GETTING_STARTED.md의 문제 해결 섹션](./docs/GETTING_STARTED.md#troubleshooting)을 확인하세요.

### Q: OpenClaw와 뭐가 다르죠?
A: OpenClaw는 AI 에이전트, OC-Memory는 기억 시스템입니다.
   - OpenClaw: "지금 뭐 할까?"
   - OC-Memory: "지난번엔 이렇게 했는데..."

### Q: 얼마나 오래 기억해요?
A: 기본 설정으로 90일 이상 보관합니다.

### Q: 프로덕션 환경에서 쓸 수 있나요?
A: 네! 현재 프로덕션 준비 완료 상태입니다.
   [DEPLOYMENT.md](./docs/DEPLOYMENT.md)를 참고하세요.

---

## 🤝 기여하기

버그 리포트, 기능 제안, PR 환영합니다!

1. Fork the repository
2. Create feature branch: `git checkout -b feature/YourFeature`
3. Commit: `git commit -m 'Add YourFeature'`
4. Push: `git push origin feature/YourFeature`
5. Open Pull Request

---

## 📄 라이선스

MIT License - [LICENSE](LICENSE) 파일 참조

---

## 🙌 참고

- **[Mastra Observational Memory](https://mastra.ai/docs/memory/observational-memory)** - 영감 제공
- **[OpenClaw](https://openclaw.ai/)** - AI 에이전트 프레임워크
- **[ChromaDB](https://www.trychroma.com/)** - 벡터 데이터베이스

---

**🎯 지금 바로 시작하세요!** → [GETTING_STARTED.md](./docs/GETTING_STARTED.md)
