# 🌿 Daon(다온) — 대화형 정서지지 챗봇

> 감정 분류기와 위기 탐지 게이트를 결합한 안전 우선(Safety-First) 멘탈케어 챗봇

> 다온이란? 순우리말: 좋은 일이 다 온다.

[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)]()
[![PyTorch](https://img.shields.io/badge/PyTorch-HuggingFace-ee4c2c.svg)]()
[![Gemini](https://img.shields.io/badge/LLM-Gemini-4285F4.svg)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-planned-green.svg)]()
[![Status](https://img.shields.io/badge/Status-WIP-yellow.svg)]()
[![License](https://img.shields.io/badge/License-MIT-lightgrey.svg)]()

---

## 📌 프로젝트 개요

Daon은 사용자의 감정 상태를 분석하고 정서적 지지를 제공하는 대화형 챗봇입니다.
LLM에 모든 판단을 맡기지 않고, **직접 학습한 감정 분류기**와 **위기 탐지 게이트**를 앞단에 두어
위험 신호를 놓치지 않는 구조를 목표로 합니다.

### 핵심 설계 원칙

| 원칙 | 설명 |
|------|------|
| **Safety-First** | 위기 판단을 LLM에 맡기지 않음. 규칙 기반 게이트가 모든 입력을 먼저 검사 |
| **미탐 > 오탐** | 위기를 놓치는 것(미탐)이 과잉 탐지(오탐)보다 치명적. 오탐은 의도적으로 감수 |
| **Hybrid Engine** | 감정·위기 판단은 직접 구현/학습, 응답 생성은 LLM API |
| **LLM 교체 가능** | LLM 호출을 한 모듈에서만 관리하여 Gemini ↔ Claude 등 교체 시 나머지 코드 불변 |

> ⚠️ **면책 조항**: 본 프로젝트는 학습 및 포트폴리오 목적의 프로토타입입니다.
> 전문적인 의료·심리 상담을 대체하지 않으며, 위기 상황 시 전문기관(자살예방상담전화 109) 연결을 안내합니다.

---

## 📈 현재 결과

- **감정 분류기**: KoBERT 파인튜닝, 6-클래스 정확도 **57.40%** (무작위 기준 16.7% 대비 약 3.4배)
- **과적합 진단 및 개선**: Epoch별 Loss 분석으로 과적합 확인 → 3 epoch → 2 epoch 조정
  - Validation Loss 1.451 → **1.135**, 정확도 56.54% → **57.40%**
- **위기 탐지 게이트**: 규칙 기반 1차 구현 (위기 감지 + 강도 판단 + 대응)
  - 테스트 중 미탐 사례를 직접 발견·수정하며 키워드 방식의 한계를 확인 → AI 보강 과제로 정리
- **남은 과제**: 클래스 불균형(기쁨 6,126 vs 불안 9,319), 유사 감정 간 혼동(슬픔 ↔ 상처)

---

## 🏗️ 시스템 아키텍처

```
사용자 입력
    │
    ▼
┌──────────────────┐
│  위기 탐지 게이트   │  위기 표현 감지 (문장 길이와 무관하게 검사)
└────────┬─────────┘
         │
    ┌────┴─────────────────────┐
    │ 위기 O                     │ 위기 X
    ▼                          ▼
┌──────────────┐        ┌──────────────┐
│  강도 판단     │        │  감정 분류기   │  분노·슬픔·불안·상처·당황·기쁨
└──────┬───────┘        └──────┬───────┘
       │                       │
  ├─ high: 공감 + 즉시 전문기관 안내   ▼
  └─ medium: 공감 + 열린 질문   ┌──────────────┐
     (대화는 끊지 않음)          │  LLM 응답 생성  │  감정 라벨을 프롬프트에 주입
                              └──────────────┘
```

### 컴포넌트 역할

| 컴포넌트 | 구현 방식 | 상태 |
|---------|----------|------|
| 위기 탐지 | 규칙 기반 (위기 신호 / 임박 신호 분리) | ✅ 1차 완료, AI 보강 연계 |
| 감정 분류 | KoBERT 파인튜닝 (6-클래스) + Gemini 하이브리드 교차 검증 | ✅ 완료 |
| 응답 생성 | Gemini API + 감정 주입 공감 프롬프트 | ✅ 완료 |
| 대화 플랫폼 | Streamlit (마음 날씨 이모지 위젯 + 감정 스펙트럼) | ✅ 완료 |
| 백엔드 통합 | FastAPI (REST API 엔드포인트) | ⏳ 예정 |
| 감정 로그 | Oracle (세션별 감정 변화 기록) | ⏳ 예정 |

---

## 🛠️ 기술 스택

| 영역 | 기술 | 선택 이유 |
|------|------|----------|
| **ML / NLP** | PyTorch, HuggingFace Transformers, KoBERT | 한국어 감정 분류기 파인튜닝 |
| **Data** | pandas, NumPy | 5.2만 건 JSON 전처리 및 결과 분석 |
| **학습 환경** | Google Colab (T4 GPU) | 무료 GPU로 학습 시간 단축 |
| **LLM** | Google **Gemini API** (`google-genai`) | 공감 응답 생성 및 저신뢰도 감정 교차 검증 |
| **Frontend** | **Streamlit** (현재) → JavaScript (예정) | 프로토타입 빠른 검증 후 웹 확장 |
| **Backend** | FastAPI (예정) | ML/LLM 엔진을 독립 API로 서빙 |
| **Database** | Oracle + `oracledb` (예정) | 기존 보유 환경 활용 |

> 💡 **프론트엔드 전략**: Streamlit으로 작동하는 플랫폼을 확보한 뒤 향후 JavaScript/React로 전환합니다.
> 코어 엔진(`app/core/engine.py`)이 모듈화되어 있어 프론트가 바뀌어도 그대로 재사용됩니다.

---

## 📊 데이터셋

| 데이터셋 | 용도 | 상태 |
|---------|------|------|
| AI Hub 감성대화 말뭉치 | 감정 분류 학습 (51,628건) | ✅ 사용 중 |
| AI Hub 웰니스 대화 스크립트 | 상담 톤 / 프롬프트 참고 | ⏳ 예정 |
| KOTE | 한국어 감정 태깅 (보강용) | ⏳ 검토 중 |

> 감성대화 말뭉치의 세부 감정 60개를 **대분류 6개**로 재구성했습니다.
> 학습 난이도를 낮추고, 서비스 목적(사용자 상태 파악)에는 대분류로 충분하다고 판단했습니다.

---

## 📂 프로젝트 구조

```
Daon/
├── app/
│   ├── ui.py                # 🌿 Streamlit 대화형 플랫폼 (마음 날씨/감정 차트) ✅
│   └── core/
│       ├── crisis_gate.py   # 🛡️ 위기 탐지 게이트 (Safety Gate)            ✅
│       ├── emotion.py       # 🎭 6-클래스 감정분류 + Gemini 하이브리드 검증   ✅
│       ├── llm.py           # 💬 Gemini 공감 응답 생성기                   ✅
│       └── engine.py        # ⚙️ 3단계 안전 통합 오케스트레이터             ✅
├── src/
│   ├── crisis_gate.py       # 위기 탐지 게이트 1차 프로토타입
│   ├── explore.py           # 데이터 탐색 스크립트
│   ├── llm_test.py          # Gemini API 호출 테스트
│   └── process.py           # AI Hub 데이터 전처리 파이프라인
├── data/                    # 데이터셋 (gitignore)
├── Daon.ipynb               # KoBERT 파인튜닝 학습 노트북 (Colab)
├── .env                     # API 키 (gitignore)
├── requirements.txt         # 필수 라이브러리 목록
└── README.md
```

> 학습된 모델 가중치는 용량 문제로 레포에 포함하지 않습니다.

---

## 🗺️ 로드맵

- [x] **Phase 2** — 데이터 준비 (AI Hub 감성대화 5.2만 건 수집·전처리)
- [x] **Phase 3** — 감정 분류기 학습 (KoBERT 파인튜닝, Acc 57.40%)
- [x] **Phase 4** — 위기 탐지 게이트 (규칙 기반, 강도 분기)
- [x] **Phase 5** — LLM 연동 & 프롬프트 설계 & 하이브리드 교차 검증 (Gemini) ✅
- [ ] **Phase 6** — FastAPI 백엔드 통합 + Oracle 연동
- [x] **Phase 7** — Streamlit MVP 플랫폼 (마음 날씨 + 감정 스펙트럼) ✅
- [ ] **Phase 8~9** — JavaScript 프론트엔드 전환 & 배포

---

## 🚀 실행 방법

```bash
# 1. 가상환경 생성 및 활성화
python -m venv venv
venv\Scripts\activate            # macOS/Linux: source venv/bin/activate

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 환경 변수 설정 (.env 파일 생성)
# GEMINI_API_KEY=your_gemini_api_key

# 4. Streamlit 대화형 챗봇 플랫폼 실행
streamlit run app/ui.py
```

---

## ⚠️ 한계 및 주의사항

- **키워드 방식의 한계**: 규칙 기반 게이트는 우회적·개인적인 위기 표현을 모두 잡을 수 없으며,
  "배고파 죽겠다" 같은 관용 표현도 위기로 탐지할 수 있습니다. 문맥을 이해하는 AI 보강이 필요합니다.
- **전문 영역**: 자살·자해 신호 탐지는 임상 근거가 필요한 영역입니다.
  실서비스 단계에서는 전문기관이 검증한 기준과 전문가 자문이 반드시 필요합니다.

---

## 📝 개발 기록

> 단계별 학습 과정, 트러블슈팅, 설계 판단은 [Notion 개발 위키](https://app.notion.com/p/3816e89c3cfa815b9c2ff663c51a9f01)에 정리합니다.

---

## 📄 License

MIT License

---

## 👤 Author

산업IT공학(ITM) | Son Jaemin



