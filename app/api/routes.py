"""FastAPI Router for Daon Core Services"""

from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends
from app.api.schemas import (
    HealthResponse,
    ChatRequest,
    ChatResponse,
    EmotionPredictRequest,
    EmotionPredictResponse,
)
from app.core.engine import DaonEngine

router = APIRouter()

# 전역 엔진 인스턴스 (지연 초기화 및 재사용)
_engine: DaonEngine = None

def get_engine() -> DaonEngine:
    global _engine
    if _engine is None:
        _engine = DaonEngine()
    return _engine

@router.get("/health", response_model=HealthResponse, tags=["System"])
def health_check(engine: DaonEngine = Depends(get_engine)):
    """시스템 헬스체크 및 코어 엔진 로드 상태 확인"""
    return HealthResponse(
        status="ok",
        version="1.0.0",
        engine_ready=(engine is not None)
    )

@router.post("/api/v1/chat", response_model=ChatResponse, tags=["Chat"])
def chat(request: ChatRequest, engine: DaonEngine = Depends(get_engine)):
    """
    3단계 안전 파이프라인 대화 엔드포인트
    1단계: 위기 탐지 게이트 (Safety Gate)
    2단계: 감정 분류 및 Gemini 하이브리드 교차 검증
    3단계: LLM 공감 응답 생성
    """
    try:
        # Pydantic ChatMessage 모델을 engine 형식(List[Dict[str, str]])으로 변환
        history = None
        if request.chat_history:
            history = [{"role": msg.role, "content": msg.content} for msg in request.chat_history]

        result = engine.process_message(
            user_message=request.message,
            chat_history=history
        )
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"챗봇 엔진 처리 중 오류가 발생했습니다: {str(e)}")

@router.post("/api/v1/predict-emotion", response_model=EmotionPredictResponse, tags=["Emotion"])
def predict_emotion(request: EmotionPredictRequest, engine: DaonEngine = Depends(get_engine)):
    """단독 텍스트 감정 분석 (하이브리드 교차 검증 포함)"""
    try:
        top_emotion, confidence, emotion_scores, meta = engine.emotion_classifier.predict(
            text=request.text,
            gemini_client=engine.llm_service.client
        )
        return EmotionPredictResponse(
            text=request.text,
            top_emotion=top_emotion,
            confidence=confidence,
            emotion_scores=emotion_scores,
            cross_validated=meta.get("is_cross_validated", False),
            validation_reason=meta.get("validation_reason")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"감정 분석 처리 중 오류가 발생했습니다: {str(e)}")
