"""Pydantic Request & Response Schemas for Daon API"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class HealthResponse(BaseModel):
    status: str = Field(..., examples=["ok"])
    version: str = Field(..., examples=["1.0.0"])
    engine_ready: bool = Field(..., examples=[True])

class ChatMessage(BaseModel):
    role: str = Field(..., description="발화 주체 ('user' 또는 'assistant')", examples=["user"])
    content: str = Field(..., description="대화 메시지 내용", examples=["오늘 회사에서 너무 지치고 힘들었어."])

class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="사용자 입력 문장", examples=["오늘 하루가 너무 버겁고 지쳐."])
    chat_history: Optional[List[ChatMessage]] = Field(default=None, description="이전 대화 히스토리")
    session_id: Optional[str] = Field(default=None, description="대화 세션 식별자 (로그/통계용)")

class ChatResponse(BaseModel):
    response: str = Field(..., description="챗봇 또는 안전 게이트 대응 메시지")
    is_crisis: bool = Field(..., description="위기 신호 감지 여부")
    crisis_level: Optional[str] = Field(default=None, description="위기 심각도 ('high', 'medium', None)")
    crisis_reason: str = Field(..., description="위기 판정 사유")
    matched_keywords: List[str] = Field(default_factory=list, description="매칭된 위기/임박 키워드")
    emotion: str = Field(..., description="분석된 핵심 감정 (분노, 슬픔, 불안, 상처, 당황, 기쁨, 위기/절박)")
    emotion_confidence: float = Field(..., description="감정 신뢰도 (0.0 ~ 1.0)")
    emotion_scores: Dict[str, float] = Field(default_factory=dict, description="6대 감정별 확률 점수")
    source: str = Field(..., description="응답 생성 주체 ('crisis_gate' 또는 'llm')")
    cross_validated: bool = Field(..., description="Gemini 하이브리드 교차 검증 적용 여부")
    validation_reason: Optional[str] = Field(default=None, description="교차 검증 사유 또는 추론 근거")

class EmotionPredictRequest(BaseModel):
    text: str = Field(..., min_length=1, description="분석할 텍스트", examples=["동기들은 다 승진하는데 나만 제자리인 것 같아."])

class EmotionPredictResponse(BaseModel):
    text: str = Field(..., description="분석 대상 텍스트")
    top_emotion: str = Field(..., description="예측 감정")
    confidence: float = Field(..., description="신뢰도")
    emotion_scores: Dict[str, float] = Field(default_factory=dict, description="감정별 확률 분포")
    cross_validated: bool = Field(..., description="교차 검증 적용 여부")
    validation_reason: Optional[str] = Field(default=None, description="교차 검증 사유")
