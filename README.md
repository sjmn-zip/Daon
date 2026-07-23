# 🌿 Daon(다온) — 대화형 정서지지 챗봇

> 감정 분류기와 위기 탐지 게이트를 결합한 안전 우선(safety-first) 멘탈케어 챗봇

> 다온이란? 순우리말: 좋은 일이 다 온다.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-0.11x-green.svg)]()
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-red.svg)]()
[![Oracle](https://img.shields.io/badge/Oracle-DB-orange.svg)]()
[![Status](https://img.shields.io/badge/Status-WIP-yellow.svg)]()
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)]()

---

## 📌 프로젝트 개요

Daon은 사용자의 감정 상태를 분석하고 정서적 지지를 제공하는 대화형 챗봇입니다.
단순히 LLM에 응답을 위임하는 것이 아니라, **직접 학습한 감정 분류기**와 **위기 탐지 게이트**를 앞단에 두어
위험 신호를 놓치지 않는 구조를 목표로 합니다.

### 핵심 설계 원칙

| 원칙 | 설명 |
|------|------|
| **Safety-First** | LLM이 위기 상황을 단독 판단하지 않음. 별도 분류기가 먼저 필터링 |
| **Hybrid Engine** | 대화 생성은 LLM API, 감정/위기 판단은 직접 학습 모델 |
| **Observable** | 모든 세션의 감정 변화를 로깅하여 추후 대시보드 확장 가능 |

> ⚠️ **면책 조항**: 본 프로젝트는 학습 및 포트폴리오 목적의 프로토타입입니다.
> 전문적인 의료·심리 상담을 대체하지 않으며, 위기 상황 시 전문기관(자살예방상담전화 109) 연결을 안내합니다.

---

## 🏗️ 시스템 아키텍처

```
                    ┌─────────────────┐
   사용자 입력 ───→ │  위기 탐지 게이트  │ ──위험──→ 전문기관 안내 + 대화 중단
                    └────────┬────────┘
                             │ 안전
                    ┌────────▼────────┐
                    │   감정 분류기     │ ──→ 감정 라벨 (예: 불안, 우울, 분노)
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  LLM 응답 생성   │ ──→ 감정 라벨을 프롬프트에 주입
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │  감정 로그 저장   │ ──→ Oracle (세션별 시계열)
                    └─────────────────┘
```

### 컴포넌트 역할 분리

| 컴포넌트 | 구현 방식 | 비고 |
|---------|----------|------|
| 대화 생성 | LLM API (Claude / GPT) | 프롬프트 엔지니어링 |
| 감정 분류 | KoBERT 파인튜닝 | **직접 학습** (DS 핵심) |
| 위기 탐지 | 규칙 + 분류기 | 자살/자해 신호 탐지 |
| 상태 추적 | SQL + 규칙 | 세션별 감정 변화 |

---

## 🛠️ 기술 스택

> **언어 전략**: 프로젝트 전체를 **Python 단일 언어**로 통일했습니다.
> 백엔드·ML·프론트를 한 언어로 묶으면 컨텍스트 전환 비용이 사라지고,
> 파이썬 재학습이 곧 전 영역 학습으로 직결됩니다. (포트폴리오 완성도 최우선 전략)

| 영역 | 언어 / 기술 | 선택 이유 |
|------|------------|----------|
| **Backend** | Python + **FastAPI** | ML 코드와 동일 언어 → 통합 자연스러움, 비동기 처리 |
| **ML / NLP** | Python + **HuggingFace Transformers** | 감정 분류기 직접 학습 (KoBERT / KcELECTRA) |
| **Frontend** | Python + **Streamlit** | JS 학습 비용 없이 Python만으로 데모 UI 구현 |
| **Database** | **Oracle** (SQL*Plus) + `oracledb` | 보유 환경 활용, SQL 역량 적용 |
| **LLM** | Anthropic **Claude API** | 공감적 응답 생성 |

### 언어 선택 노트

- **JavaScript / React는 의도적으로 제외**했습니다. 방학 기간 내 완성도를 위해 학습 대상을 (파이썬·HuggingFace·FastAPI)로 한정하고, 프론트는 Python(Streamlit)으로 해결합니다.
- **Oracle 연동**은 `oracledb` 라이브러리를 사용합니다. SQL*Plus 환경이 이미 구축되어 있어 별도 DB 설치 없이 진행 가능합니다.
- 추후 확장 시(실서비스 단계) 프론트를 React로 분리하는 것을 고려할 수 있습니다.

---

## 📂 프로젝트 구조

```
mindcare-ai/
├── app/
│   ├── main.py              # FastAPI 엔트리포인트
│   ├── ui.py                # Streamlit 프론트엔드 (데모)
│   ├── core/
│   │   ├── crisis_gate.py   # 위기 탐지 게이트
│   │   ├── emotion.py       # 감정 분류 추론
│   │   └── llm.py           # LLM 응답 생성
│   ├── models/              # 학습된 모델 가중치
│   └── db/
│       └── schema.sql       # Oracle DB 스키마 (DDL)
├── ml/
│   ├── train_emotion.py     # 감정 분류기 학습 스크립트
│   └── notebooks/           # 데이터 탐색 / 실험
├── data/                    # 데이터셋 (gitignore)
├── tests/
├── requirements.txt
└── README.md
```

---

## 📊 데이터셋

| 데이터셋 | 용도 | 출처 |
|---------|------|------|
| AI Hub 감성대화 말뭉치 | 감정 분류 학습 | AI Hub (60개 감정 라벨) |
| AI Hub 웰니스 대화 | 상담 톤 / 프롬프트 | AI Hub |
| KOTE | 한국어 감정 태깅 | GitHub 공개 (50개 라벨) |

---

## 🗺️ 로드맵

> 처음 진행하는 개발 프로젝트이므로, 각 Phase가 **한 번에 하나의 목표**만 갖도록 잘게 나눴습니다.
> 3개 트랙으로 구성: **기반 → 코어(본체) → 확장(JS 풀스택 전환)**

### 🧱 기반 트랙 — 개발 환경과 파이썬 기초

- [x] **Phase 0** — 개발 환경 세팅
  - [x] 0-1. Python 설치 확인
  - [x] 0-2. VSCode 준비 (확장 설치)
  - [x] 0-3. 프로젝트 폴더 + Git 초기화
  - [x] 0-4. 가상환경(venv) 생성
  - [x] 0-5. GitHub 레포 연결
- [x] **Phase 1** — 파이썬 재학습
  - [x] 1-1. 기본 문법 복습 (자료형·조건문·반복문)
  - [x] 1-2. 함수와 클래스 (Java 경험과 비교)
  - [x] 1-3. pandas로 데이터 다뤄보기

### ⚙️ 코어 트랙 — AI 엔진과 백엔드 (프로젝트 본체)

- [x] **Phase 2** — 데이터 준비
  - [x] 2-1. AI Hub 감성대화 데이터 수집
  - [x] 2-2. 데이터 탐색 및 전처리
- [ ] **Phase 3** — 감정 분류기 학습 (KoBERT 파인튜닝)
- [ ] **Phase 4** — 위기 탐지 게이트 구현 (규칙 → 분류기)
- [ ] **Phase 5** — LLM 연동 & 프롬프트 설계
- [ ] **Phase 6** — FastAPI 백엔드 통합 + Oracle 연동

### 🚀 확장 트랙 — 데모부터 JS 풀스택까지

- [ ] **Phase 7** — Streamlit MVP (작동하는 데모 확보 ✅)
  - [ ] 7-1. Streamlit 기본 화면
  - [ ] 7-2. FastAPI 백엔드 연결
  - [ ] 7-3. 감정 로깅(Oracle) 연동
- [ ] **Phase 8** — JavaScript 학습 (신규 도전)
  - [ ] 8-1. HTML / CSS 기초
  - [ ] 8-2. JavaScript 기초 (변수·함수·DOM)
  - [ ] 8-3. `fetch`로 FastAPI 호출 실습
  - [ ] 8-4. (선택) React 입문
- [ ] **Phase 9** — JS 프론트엔드 전환 & 고도화
  - [ ] 9-1. 챗봇 UI를 JS로 재구축
  - [ ] 9-2. 데모 배포 & 최종 문서화

> 💡 **전략 노트**: Phase 7에서 먼저 "작동하는 것"을 확보한 뒤, Phase 8~9에서 JS로 확장합니다.
> 백엔드(FastAPI)는 API라서 프론트가 Streamlit이든 JS든 그대로 재사용됩니다.
> 포트폴리오 스토리: *"MVP를 Streamlit으로 검증 후 JS로 고도화"* → 의사결정 능력 어필.

---

## 🚀 실행 방법

```bash
# 1. 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 환경 변수 설정 (.env)
# ANTHROPIC_API_KEY=your_key
# ORACLE_USER=...
# ORACLE_PASSWORD=...
# ORACLE_DSN=localhost:1521/xe

# 4. 백엔드 서버 실행
uvicorn app.main:app --reload

# 5. 프론트(데모) 실행
streamlit run app/ui.py
```

> ⚠️ `.env`(API 키, DB 비밀번호)는 **절대 커밋하지 마십시오.** 환경변수로 관리하는 것을 권장합니다.

---

## 📝 학습 기록

> 파이썬 재학습 과정과 모델 실험 결과는 [Notion 기술 블로그](https://app.notion.com/p/3816e89c3cfa815b9c2ff663c51a9f01)에 정리합니다.

---

## 📄 License

MIT License

---

## 👤 Author

산업IT공학(ITM) | Son Jaemin


