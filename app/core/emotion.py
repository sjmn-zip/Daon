"""감정 분류 추론 모듈 (Emotion Classifier & Hybrid Verifier)

사용자의 발화를 6가지 핵심 감정(분노, 슬픔, 불안, 상처, 당황, 기쁨)으로 분류합니다.
1차로 로컬 모델/사전 기반 빠른 분류를 수행하고,
신뢰도가 낮거나 애매한 경우(Confidence < 0.65) Gemini LLM을 통한
2차 하이브리드 교차 검증(Hybrid Cross-Validation)을 수행하여 정확도를 극대화합니다.
"""

import os
import json
import re
from typing import Dict, Tuple, Any

EMOTIONS = ["분노", "슬픔", "불안", "상처", "당황", "기쁨"]

EMOTION_EMOJIS = {
    "분노": "😡",
    "슬픔": "😢",
    "불안": "😰",
    "상처": "💔",
    "당황": "😳",
    "기쁨": "😊",
    "중립/평온": "🌿"
}

EMOTION_COLORS = {
    "분노": "#FF4B4B",
    "슬픔": "#1E88E5",
    "불안": "#FB8C00",
    "상처": "#8E24AA",
    "당황": "#00ACC1",
    "기쁨": "#43A047",
    "중립/평온": "#66BB6A"
}

class EmotionClassifier:
    def __init__(self, model_dir: str = "models/kobert"):
        self.model_dir = model_dir
        self.model = None
        self.tokenizer = None
        
        # 감정 사전 (1차 빠른 스크리닝용)
        self.lexicon = {
            "분노": ["화나", "짜증", "빡치", "열받", "억울", "분통", "욕나", "지긋지긋", "미치겠", "개빡", "답답"],
            "슬픔": ["눈물", "슬프", "울고", "울었", "비참", "우울", "적적", "공허", "가슴이 찢", "먹먹", "외로", "쓸쓸"],
            "불안": ["불안", "초조", "걱정", "두렵", "무섭", "떨려", "망할까", "어쩌지", "조마조마", "긴장", "패닉"],
            "상처": ["서운", "배신", "상처", "마음 아파", "괴로", "서글", "무시", "소외", "비수", "모욕"],
            "당황": ["당황", "황당", "어이없", "멘붕", "놀랐", "어안이 벙벙", "충격", "갑자기 왜"],
            "기쁨": ["기뻐", "행복", "즐거", "신나", "뿌듯", "다행", "감사", "좋았", "설레", "웃음", "희망", "최고"]
        }
        
        self._load_local_model_if_available()

    def _load_local_model_if_available(self):
        """로컬에 파인튜닝된 KoBERT 가중치 폴더가 있을 경우 로드"""
        if os.path.exists(self.model_dir) and any(os.scandir(self.model_dir)):
            try:
                from transformers import AutoTokenizer, AutoModelForSequenceClassification
                self.tokenizer = AutoTokenizer.from_pretrained(self.model_dir)
                self.model = AutoModelForSequenceClassification.from_pretrained(self.model_dir)
                self.model.eval()
                print(f"[EmotionClassifier] 로컬 KoBERT 모델 로드 완료: {self.model_dir}")
            except Exception as e:
                print(f"[EmotionClassifier] 로컬 모델 로드 실패: {e}")

    def predict_primary(self, text: str) -> Tuple[str, float, Dict[str, float]]:
        """1차 추론 (KoBERT 가중치 또는 사전 기반 휴리스틱)"""
        if self.model and self.tokenizer:
            try:
                import torch
                inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=64)
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    probs = torch.softmax(outputs.logits, dim=1).squeeze().tolist()
                scores = {EMOTIONS[i]: float(probs[i]) for i in range(len(EMOTIONS))}
                top_emotion = max(scores, key=scores.get)
                return top_emotion, scores[top_emotion], scores
            except Exception as e:
                print(f"[EmotionClassifier] KoBERT 추론 오류: {e}")

        # 사전 기반 추론
        scores = {emo: 0.05 for emo in EMOTIONS}
        text_clean = text.strip()
        matched = False

        for emo, words in self.lexicon.items():
            for word in words:
                if word in text_clean:
                    scores[emo] += 0.4
                    matched = True

        total = sum(scores.values())
        normalized_scores = {k: round(v / total, 3) for k, v in scores.items()}
        top_emotion = max(normalized_scores, key=normalized_scores.get)
        confidence = normalized_scores[top_emotion]

        if not matched or confidence <= 0.25:
            return "중립/평온", 0.3, normalized_scores

        return top_emotion, confidence, normalized_scores

    def cross_validate_with_gemini(self, text: str, client: Any) -> Dict[str, Any]:
        """Gemini를 이용한 2차 제로샷 감정 교차 검증"""
        if not client:
            return None

        prompt = f"""당신은 심리언어학 기반의 한국어 감정 분석 전문가입니다.
다음 발화에서 가장 짙게 드러나는 감정을 분석해 주세요.

[사용자 발화]
"{text}"

[분류 대상 감정 목록 (반드시 이 중에서만 1개 선택)]
- 분노
- 슬픔
- 불안
- 상처
- 당황
- 기쁨
- 중립/평온

[응답 규칙]
- 반드시 유효한 JSON 형식 하나만 출력하세요. 마크다운이나 추가 설명 금지.
형식:
{{
  "emotion": "감정명",
  "confidence": 0.85,
  "reason": "선택한 핵심 단어 및 문맥 이유 한 줄"
}}
"""
        try:
            interaction = client.interactions.create(
                model="gemini-3.8-flash",
                input=prompt
            )
            raw = interaction.output_text.strip()
            # JSON 블록 정제
            match = re.search(r'\{.*\}', raw, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                emotion = data.get("emotion")
                if emotion in EMOTIONS or emotion == "중립/평온":
                    confidence = float(data.get("confidence", 0.85))
                    return {
                        "emotion": emotion,
                        "confidence": confidence,
                        "reason": data.get("reason", "")
                    }
        except Exception as e:
            print(f"[EmotionClassifier] Gemini 교차 검증 실패: {e}")
        return None

    def predict(self, text: str, gemini_client: Any = None) -> Tuple[str, float, Dict[str, float], Dict[str, Any]]:
        """
        1차 추론 후 신뢰도 < 0.65 또는 중립/평온일 때 Gemini로 2차 교차 검증 수행.
        반환: (최종감정, 신뢰도, 감정별점수, 검증메타정보)
        """
        top_emotion, confidence, scores = self.predict_primary(text)
        meta = {
            "is_cross_validated": False,
            "validation_reason": "1차 모델 단독 판정",
            "primary_emotion": top_emotion,
            "primary_confidence": confidence
        }

        # 신뢰도가 0.65 미만이거나 중립으로 애매할 때 Gemini 교차 검증 발동
        if (confidence < 0.65 or top_emotion == "중립/평온") and gemini_client is not None:
            cv_res = self.cross_validate_with_gemini(text, gemini_client)
            if cv_res:
                top_emotion = cv_res["emotion"]
                confidence = cv_res["confidence"]
                meta["is_cross_validated"] = True
                meta["validation_reason"] = cv_res["reason"]

                # 점수 재분배
                if top_emotion in scores:
                    scores = {e: 0.05 for e in EMOTIONS}
                    scores[top_emotion] = round(confidence, 3)
                    rem = round((1.0 - confidence) / (len(EMOTIONS) - 1), 3)
                    for e in EMOTIONS:
                        if e != top_emotion:
                            scores[e] = rem

        return top_emotion, confidence, scores, meta
