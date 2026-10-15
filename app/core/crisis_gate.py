"""위기 신호 탐지 게이트 (Safety Gate)

LLM 응답 생성 전 1차 방어선으로 동작하며, 
자살·자해 등 심각한 위험 신호를 규칙 기반으로 감지하여 안전망을 제공합니다.
"""

class CrisisGate:
    def __init__(self):
        # 1차 위기 신호 키워드
        self.crisis_keywords = [
            "죽고 싶", "사라지고 싶", "살기 싫", "더 못 버티", "더는 못 버티",
            "죽으려", "죽어버리", "세상을 떠나", "끝내고 싶", "극단적", "자해", "목숨"
        ]
        
        # 임박 신호 (구체적 방법, 시점, 실행 도구 → 무조건 고위험)
        self.imminent_keywords = [
            "지금", "오늘", "방법", "유서", "준비했", "약", "번개탄", "투신", "옥상"
        ]

    def check(self, text: str) -> dict:
        """위기 여부와 위험 강도를 판단하여 딕셔너리로 반환"""
        text_clean = text.strip()
        matched_crisis = [kw for kw in self.crisis_keywords if kw in text_clean]

        if not matched_crisis:
            return {
                "crisis": False,
                "level": None,
                "matched_keywords": [],
                "reason": "정상"
            }

        # 임박 신호 검사
        matched_imminent = [kw for kw in self.imminent_keywords if kw in text_clean]
        
        if matched_imminent:
            return {
                "crisis": True,
                "level": "high",
                "matched_keywords": matched_crisis + matched_imminent,
                "reason": f"임박 신호 감지 ({', '.join(matched_imminent)})"
            }

        # 임박 신호가 없을 때 문장 길이로 판단 (짧고 단호할수록 고위험)
        if len(text_clean) <= 15:
            return {
                "crisis": True,
                "level": "high",
                "matched_keywords": matched_crisis,
                "reason": "단문 고위험 표현"
            }
        else:
            return {
                "crisis": True,
                "level": "medium",
                "matched_keywords": matched_crisis,
                "reason": "심리적 위기 표현 감지"
            }

    def get_response(self, level: str) -> str:
        """위기 강도에 따른 안전 가이드 및 공감 대응 메시지"""
        if level == "high":
            return (
                "지금 너무나 깊은 고통 속에 계신 것 같아 많이 걱정스럽습니다. 혼자 짊어지지 않으셔도 괜찮아요.\n\n"
                "**24시간 언제든 도움을 줄 수 있는 전문가가 기다리고 있습니다.**\n"
                "- 📞 **자살예방상담전화: 109** (24시간 무료)\n"
                "- 📞 **정신건강위기상담전화: 1577-0199**\n\n"
                "지금 바로 전화 한 번 걸어보시겠어요? 제가 곁에서 함께 기다릴게요."
            )
        elif level == "medium":
            return (
                "요즘 마음이 정말 무겁고 많이 지치신 것 같아요. 그런 힘든 생각이 드는 것도 무리가 아니에요.\n\n"
                "가슴속에 담아둔 힘든 이야기들을 조금만 저에게 털어놓아 주실 수 있나요? 편안하게 들려주세요. 제가 온전히 들을게요."
            )
        return ""
