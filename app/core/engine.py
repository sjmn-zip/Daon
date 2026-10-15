"""Daon Core Engine (통합 오케스트레이터)

위기 탐지 게이트 -> 감정 분류기 (하이브리드 교차 검증) -> LLM 응답 생성을 유기적으로 연결합니다.
"""

from typing import Dict, Any, List
from app.core.crisis_gate import CrisisGate
from app.core.emotion import EmotionClassifier, EMOTIONS
from app.core.llm import LLMService

class DaonEngine:
    def __init__(self, model_name: str = "gemini-3.8-flash"):
        self.crisis_gate = CrisisGate()
        self.emotion_classifier = EmotionClassifier()
        self.llm_service = LLMService(model_name=model_name)

    def process_message(
        self,
        user_message: str,
        chat_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """사용자 메시지를 3단계 안전 파이프라인으로 처리"""
        # 1단계: 위기 탐지 게이트 (Safety Gate)
        crisis_info = self.crisis_gate.check(user_message)
        
        if crisis_info["crisis"]:
            crisis_response = self.crisis_gate.get_response(crisis_info["level"])
            return {
                "response": crisis_response,
                "is_crisis": True,
                "crisis_level": crisis_info["level"],
                "crisis_reason": crisis_info["reason"],
                "matched_keywords": crisis_info["matched_keywords"],
                "emotion": "위기/절박",
                "emotion_confidence": 1.0,
                "emotion_scores": {e: 0.0 for e in EMOTIONS},
                "source": "crisis_gate",
                "cross_validated": False,
                "validation_reason": "위기 게이트 즉시 차단"
            }

        # 2단계: 감정 분류 및 Gemini 하이브리드 교차 검증
        top_emotion, confidence, emotion_scores, meta = self.emotion_classifier.predict(
            text=user_message,
            gemini_client=self.llm_service.client
        )

        # 3단계: LLM 공감 응답 생성
        llm_response = self.llm_service.generate_response(
            user_message=user_message,
            detected_emotion=top_emotion,
            confidence=confidence,
            chat_history=chat_history
        )

        return {
            "response": llm_response,
            "is_crisis": False,
            "crisis_level": None,
            "crisis_reason": "정상",
            "matched_keywords": [],
            "emotion": top_emotion,
            "emotion_confidence": confidence,
            "emotion_scores": emotion_scores,
            "source": "llm",
            "cross_validated": meta["is_cross_validated"],
            "validation_reason": meta["validation_reason"]
        }
