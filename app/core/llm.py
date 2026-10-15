"""LLM 응답 생성 모듈 (Gemini API)

사용자의 감정 라벨과 대화 맥락을 시스템 프롬프트에 동적으로 주입하여,
평가나 조언 대신 깊은 공감과 심리적 지지를 전달하는 안전한 응답을 생성합니다.
"""

import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self, model_name: str = "gemini-3.8-flash"):
        self.model_name = model_name
        self._init_client()

    def _init_client(self):
        try:
            from google import genai
            self.client = genai.Client()
        except Exception as e:
            print(f"[LLMService] 클라이언트 초기화 실패: {e}")
            self.client = None

    def generate_response(
        self,
        user_message: str,
        detected_emotion: str,
        confidence: float,
        chat_history: List[Dict[str, str]] = None
    ) -> str:
        """감정 정보를 주입한 공감 응답 생성"""
        if not self.client:
            return "죄송합니다. 현재 언어 모델 연결에 일시적인 문제가 발생했습니다. 조금 뒤 다시 시도해 주세요."

        # 최근 대화 히스토리 (최대 4턴 반영)
        history_text = ""
        if chat_history:
            recent_turns = chat_history[-6:]
            formatted = []
            for msg in recent_turns:
                role = "사용자" if msg["role"] == "user" else "다온"
                formatted.append(f"{role}: {msg['content']}")
            history_text = "\n[최근 대화 흐름]\n" + "\n".join(formatted) + "\n"

        prompt = f"""당신은 사용자의 마음을 보듬어주는 전문적인 정서 지지 챗봇 '다온(Daon)'입니다.
'다온'은 '좋은 일이 다 온다'라는 순우리말로, 안전 우선(Safety-First)의 정서적 버팀목 역할을 합니다.

[사용자 감정 분석 결과]
- 탐지된 감정: {detected_emotion} (신뢰도: {confidence * 100:.1f}%)

{history_text}
[사용자의 현재 메시지]
"{user_message}"

[응답 작성 원칙]
1. 절대 사용자를 섣불리 평가하거나 훈계, 충고하려 들지 마세요.
2. 탐지된 감정({detected_emotion})을 온전히 인정하고 수용하는 공감의 말을 건네세요.
3. 긍정 강요("힘내세요", "더 힘든 사람도 있어요")는 금물입니다.
4. 따뜻하고 자연스러운 한국어 구어체(존댓말)로 3~5문장 내외로 다정하게 답변하세요.
5. 마지막에는 사용자가 원할 경우 마음을 더 털어놓을 수 있도록 부드러운 열린 질문이나 지지의 한마디를 덧붙이세요.
"""

        try:
            interaction = self.client.interactions.create(
                model=self.model_name,
                input=prompt
            )
            return interaction.output_text
        except Exception as e:
            return f"응답 생성 중 오류가 발생했습니다: {str(e)}"
