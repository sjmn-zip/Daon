"""Daon(다온) — 대화형 정서지지 챗봇 Streamlit UI

감정 이모지 테마, 마음 날씨 위젯, 안전 우선(Safety-First) 위기 탐지 게이트,
그리고 Gemini 하이브리드 교차 검증을 갖춘 감성 인터페이스입니다.
"""

import sys
import os
import streamlit as st
import pandas as pd

# 프로젝트 루트 경로 추가
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from app.core.engine import DaonEngine
from app.core.emotion import EMOTION_EMOJIS, EMOTION_COLORS, EMOTIONS

st.set_page_config(
    page_title="Daon(다온) — 마음을 듣는 정서지지 챗봇",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 감정별 "마음 날씨" 메타포 매핑
EMOTION_WEATHER = {
    "기쁨": {"weather": "☀️ 맑음 햇살", "desc": "가슴 따뜻한 기쁨이 피어오르는 날", "bg": "#FFF9C4", "border": "#FBC02D"},
    "중립/평온": {"weather": "🌿 싱그러운 바람", "desc": "마음이 잔잔하고 평온한 상태", "bg": "#E8F5E9", "border": "#4CAF50"},
    "슬픔": {"weather": "🌧️ 토닥이는 단비", "desc": "지친 눈물을 흘려보내는 시간", "bg": "#E3F2FD", "border": "#2196F3"},
    "불안": {"weather": "🌫️ 자욱한 안개", "desc": "앞이 잘 보이지 않아 마음이 조마조마한 날", "bg": "#FFF3E0", "border": "#FF9800"},
    "상처": {"weather": "🩹 아물어가는 비", "desc": "가슴 한구석이 콕콕 아파오는 시간", "bg": "#F3E5F5", "border": "#AB47BC"},
    "당황": {"weather": "🌪️ 불어닥친 돌풍", "desc": "예상치 못한 일로 생각이 어지러운 날", "bg": "#E0F7FA", "border": "#00BCD4"},
    "분노": {"weather": "🌋 끓어오르는 불꽃", "desc": "마음속 답답함과 화가 가득 찬 상태", "bg": "#FFEBEE", "border": "#EF5350"},
    "위기/절박": {"weather": "🚨 긴급 피난처", "desc": "혼자 견디기 힘든 고통의 순간, 도움이 필요해요", "bg": "#FFCDD2", "border": "#C62828"}
}

# 커스텀 감성 CSS
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Pretendard', sans-serif;
    }
    
    .hero-header {
        background: linear-gradient(135deg, #E8F5E9 0%, #F1F8E9 50%, #E0F2F1 100%);
        padding: 24px 28px;
        border-radius: 18px;
        border: 1px solid #C8E6C9;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(46, 125, 50, 0.05);
    }
    .hero-title {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1B5E20;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .hero-subtitle {
        font-size: 1.02rem;
        color: #4E6E50;
        margin-top: 8px;
        line-height: 1.5;
    }
    .weather-card {
        padding: 16px;
        border-radius: 16px;
        margin-bottom: 16px;
        border-left: 6px solid;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: transform 0.2s ease;
    }
    .weather-card:hover {
        transform: translateY(-2px);
    }
    .badge-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        border-radius: 16px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-right: 6px;
        margin-top: 6px;
    }
    .quick-chip {
        background-color: white;
        border: 1px solid #C8E6C9;
        border-radius: 20px;
        padding: 8px 16px;
        font-size: 0.9rem;
        cursor: pointer;
        display: inline-block;
        transition: all 0.2s ease;
        margin-right: 8px;
        margin-bottom: 8px;
    }
    .quick-chip:hover {
        background-color: #E8F5E9;
        border-color: #4CAF50;
    }
    .stChatMessage {
        border-radius: 16px !important;
        margin-bottom: 10px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.02) !important;
    }
</style>
""", unsafe_allow_html=True)

# 엔진 캐싱
@st.cache_resource
def get_engine():
    return DaonEngine(model_name="gemini-3.8-flash")

engine = get_engine()

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "안녕하세요. 마음에 쉼표가 필요할 때 곁에 머무는 **다온(Daon)**입니다 🌿\n\n'좋은 일이 다 온다'는 이름처럼, 당신의 모든 이야기를 따뜻하게 품어드릴게요. 오늘 하루 어떤 마음이 머물렀나요?",
            "emotion": "중립/평온",
            "confidence": 1.0,
            "crisis": False,
            "crisis_level": None,
            "cross_validated": False
        }
    ]

if "last_analysis" not in st.session_state:
    st.session_state.last_analysis = {
        "emotion": "중립/평온",
        "confidence": 1.0,
        "emotion_scores": {e: 0.16 for e in EMOTIONS},
        "crisis": False,
        "crisis_level": None,
        "crisis_reason": "대화 대기 중",
        "matched_keywords": [],
        "cross_validated": False,
        "validation_reason": ""
    }

if "emotion_history" not in st.session_state:
    st.session_state.emotion_history = []

# ==================== 사이드바 (마음 날씨 & 실시간 분석) ====================
with st.sidebar:
    st.markdown("## 🌿 **Daon 마음 정원**")
    st.caption("Safety-First 멘탈케어 챗봇 | 다온: 좋은 일이 다 온다")
    
    st.divider()

    # 1. 오늘의 마음 날씨 카드
    curr_emo = st.session_state.last_analysis["emotion"]
    w_info = EMOTION_WEATHER.get(curr_emo, EMOTION_WEATHER["중립/평온"])
    
    st.markdown("### 🌤️ **지금 나의 마음 날씨**")
    st.markdown(f"""
    <div class="weather-card" style="background-color: {w_info['bg']}; border-left-color: {w_info['border']};">
        <div style="font-size: 1.35rem; font-weight: 700; color: #333;">{w_info['weather']}</div>
        <div style="font-size: 0.88rem; color: #555; margin-top: 5px;">{w_info['desc']}</div>
        <div style="font-size: 0.8rem; color: #777; margin-top: 8px;">
            감정 지수: <b>{EMOTION_EMOJIS.get(curr_emo, '🌿')} {curr_emo}</b> ({st.session_state.last_analysis['confidence']*100:.1f}%)
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. 위기 탐지 안전망 (Safety Gate)
    st.markdown("### 🛡️ **안전 게이트 (Safety Gate)**")
    is_crisis = st.session_state.last_analysis["crisis"]
    c_level = st.session_state.last_analysis["crisis_level"]
    
    if not is_crisis:
        st.markdown("""
        <div style="background-color: #E8F5E9; color: #2E7D32; padding: 8px 12px; border-radius: 12px; font-weight: 600; font-size: 0.88rem;">
            🟢 평온 안심 상태 (위기 신호 없음)
        </div>
        """, unsafe_allow_html=True)
    elif c_level == "medium":
        st.markdown("""
        <div style="background-color: #FFF3E0; color: #E65100; padding: 8px 12px; border-radius: 12px; font-weight: 600; font-size: 0.88rem;">
            🟡 주의 (심리적 버거움 감지)
        </div>
        """, unsafe_allow_html=True)
        st.caption(f"사유: {st.session_state.last_analysis['crisis_reason']}")
    else:
        st.markdown("""
        <div style="background-color: #FFEBEE; color: #C62828; padding: 10px 14px; border-radius: 12px; font-weight: 700; font-size: 0.92rem;">
            🔴 긴급 위험 신호 감지
        </div>
        """, unsafe_allow_html=True)
        st.error("🚨 24시간 자살예방상담전화: **109** (무료)")

    st.divider()

    # 3. 6대 감정 스펙트럼
    st.markdown("### 🎭 **감정 스펙트럼 (KoBERT + Hybrid)**")
    scores = st.session_state.last_analysis["emotion_scores"]
    
    for emo in EMOTIONS:
        score_val = scores.get(emo, 0.0)
        emoji = EMOTION_EMOJIS.get(emo, "🌿")
        st.progress(min(max(float(score_val), 0.0), 1.0), text=f"{emoji} {emo} — {score_val*100:.1f}%")

    if st.session_state.last_analysis.get("cross_validated"):
        st.info(f"⚡ **Gemini 교차 검증 발동**\n_{st.session_state.last_analysis.get('validation_reason', '')}_")

    st.divider()

    # 4. 세션 누적 감정 그래프
    st.markdown("### 📊 **오늘의 마음 그래프**")
    if st.session_state.emotion_history:
        emo_counts = pd.Series(st.session_state.emotion_history).value_counts()
        chart_df = pd.DataFrame({"감정": [f"{EMOTION_EMOJIS.get(k, '')} {k}" for k in emo_counts.index], "횟수": emo_counts.values})
        st.bar_chart(chart_df.set_index("감정"), color="#66BB6A")
    else:
        st.caption("대화가 쌓이면 마음의 흐름이 그래프로 기록됩니다 📝")

    st.divider()

    # 5. 리셋 버튼
    if st.button("🔄 마음 정원 비우기 (대화 초기화)", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "대화가 새로 시작되었습니다. 지금 어떤 마음이 머물고 있나요? 편안하게 들려주세요 🌿",
                "emotion": "중립/평온",
                "confidence": 1.0,
                "crisis": False,
                "crisis_level": None,
                "cross_validated": False
            }
        ]
        st.session_state.emotion_history = []
        st.session_state.last_analysis = {
            "emotion": "중립/평온",
            "confidence": 1.0,
            "emotion_scores": {e: 0.16 for e in EMOTIONS},
            "crisis": False,
            "crisis_level": None,
            "crisis_reason": "대화 대기 중",
            "matched_keywords": [],
            "cross_validated": False,
            "validation_reason": ""
        }
        st.rerun()

# ==================== 메인 화면 (헤더 & 이모지 퀵 체크인) ====================
st.markdown("""
<div class="hero-header">
    <div class="hero-title">🌿 Daon (다온) <span style="font-size: 1.1rem; color: #2E7D32; font-weight: 500;">— 좋은 일이 다 온다</span></div>
    <div class="hero-subtitle">
        감정 분류기와 위기 탐지 안전망이 당신의 마음을 먼저 읽고, 섣부른 조언 대신 깊은 공감을 건넵니다.
    </div>
</div>
""", unsafe_allow_html=True)

# 🌈 이모지 감정 퀵 체크인 (Quick Emotion Check-in Deck)
st.markdown("##### 💡 **지금 내 마음에 가장 가까운 감정을 골라보세요:**")
c1, c2, c3, c4, c5, c6 = st.columns(6)

selected_preset = None
if c1.button("😊 기뻐요", use_container_width=True):
    selected_preset = "오늘 기분 좋은 일이 있었어! 자랑하고 싶어서 왔어."
if c2.button("😢 슬퍼요", use_container_width=True):
    selected_preset = "오늘은 이상하게 자꾸 눈물이 나고 마음이 울적해요."
if c3.button("😰 불안해요", use_container_width=True):
    selected_preset = "앞으로 다가올 일들이 너무 걱정되고 긴장돼서 잠이 안 와요."
if c4.button("💔 상처받았어", use_container_width=True):
    selected_preset = "가까운 사람에게 큰 상처를 받아서 가슴이 콕콕 쑤셔요."
if c5.button("😡 화가 나요", use_container_width=True):
    selected_preset = "오늘 정말 불공평하고 어이없는 일을 겪어서 화가 머리끝까지 났어요."
if c6.button("😳 당황스러워", use_container_width=True):
    selected_preset = "예상치 못한 상황이 갑자기 닥쳐서 머릿속이 새하얘졌어요."

st.write("")

# 대화 메시지 렌더링
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user", avatar="💬"):
            st.write(msg["content"])
    else:
        with st.chat_message("assistant", avatar="🌿"):
            st.write(msg["content"])
            
            # 감정 태그 데코레이션
            emo = msg.get("emotion")
            if emo and emo != "중립/평온":
                emoji = EMOTION_EMOJIS.get(emo, "🌿")
                conf = msg.get("confidence", 0.0)
                is_cv = msg.get("cross_validated", False)
                
                badge_html = f"""
                <div style="margin-top: 8px;">
                    <span class="badge-pill" style="background-color: #E8F5E9; color: #2E7D32; border: 1px solid #C8E6C9;">
                        {emoji} 감정 인식: {emo} ({conf*100:.1f}%)
                    </span>
                    {"<span class='badge-pill' style='background-color: #E1F5FE; color: #0277BD; border: 1px solid #B3E5FC;'>⚡ Gemini 교차 검증</span>" if is_cv else ""}
                </div>
                """
                st.markdown(badge_html, unsafe_allow_html=True)

# 사용자 입력 수신
user_input = st.chat_input("오늘 어떤 마음이 머물렀나요? 편안하게 이야기해 주세요...")

# 이모지 퀵버튼 클릭 시 입력값 주입
if selected_preset and not user_input:
    user_input = selected_preset

if user_input:
    # 1. 유저 메시지 표시 및 상태 저장
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="💬"):
        st.write(user_input)

    # 2. 엔진 추론
    with st.chat_message("assistant", avatar="🌿"):
        with st.spinner("당신의 마음에 귀 기울이는 중... 🌿"):
            result = engine.process_message(
                user_message=user_input,
                chat_history=st.session_state.messages[:-1]
            )
            
            response_text = result["response"]
            st.write(response_text)
            
            # 감정 뱃지 표시
            emo = result["emotion"]
            if emo != "중립/평온":
                emoji = EMOTION_EMOJIS.get(emo, "🌿")
                conf = result["emotion_confidence"]
                is_cv = result.get("cross_validated", False)
                badge_html = f"""
                <div style="margin-top: 8px;">
                    <span class="badge-pill" style="background-color: #E8F5E9; color: #2E7D32; border: 1px solid #C8E6C9;">
                        {emoji} 감정 인식: {emo} ({conf*100:.1f}%)
                    </span>
                    {"<span class='badge-pill' style='background-color: #E1F5FE; color: #0277BD; border: 1px solid #B3E5FC;'>⚡ Gemini 교차 검증</span>" if is_cv else ""}
                </div>
                """
                st.markdown(badge_html, unsafe_allow_html=True)

    # 3. 세션 상태 업데이트
    st.session_state.messages.append({
        "role": "assistant",
        "content": response_text,
        "emotion": result["emotion"],
        "confidence": result["emotion_confidence"],
        "crisis": result["is_crisis"],
        "crisis_level": result["crisis_level"],
        "cross_validated": result.get("cross_validated", False)
    })

    st.session_state.last_analysis = {
        "emotion": result["emotion"],
        "confidence": result["emotion_confidence"],
        "emotion_scores": result["emotion_scores"],
        "crisis": result["is_crisis"],
        "crisis_level": result["crisis_level"],
        "crisis_reason": result["crisis_reason"],
        "matched_keywords": result["matched_keywords"],
        "cross_validated": result.get("cross_validated", False),
        "validation_reason": result.get("validation_reason", "")
    }

    if result["emotion"] not in ["중립/평온", "위기/절박"]:
        st.session_state.emotion_history.append(result["emotion"])

    st.rerun()
