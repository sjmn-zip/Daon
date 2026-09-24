class CrisisGate:
    """위기 신호를 탐지하고 강도를 판단하는 게이트 (규칙 기반)"""

    def __init__(self):
        # 위기 신호 키워드 (⚠️ 실서비스는 전문기관 검증 목록 필요)
        self.crisis_keywords = [
            "죽고 싶", "사라지고 싶", "살기 싫", "더 못 버티","죽으려", "죽어"
        ]
        # 임박 신호 (구체적 방법·시점 → 무조건 고위험)
        self.imminent_keywords = [
            "지금", "오늘", "방법", "유서", "준비했"
        ]

    def check(self, text):
        """위기 여부 + 강도 판단. 결과를 딕셔너리로 반환"""
        # 1. 위기 표현이 있는지 (길이 무관, 놓치지 않기)
        is_crisis = False
        for keyword in self.crisis_keywords:
            if keyword in text:
                is_crisis = True
                break

        if not is_crisis:
            return {"crisis": False, "level": None}

        # 2. 강도 판단
        # 2-1. 임박 신호가 있으면 무조건 고위험
        for keyword in self.imminent_keywords:
            if keyword in text:
                return {"crisis": True, "level": "high"}

        # 2-2. 임박 신호 없으면 → 길이로 판단 (짧을수록 고위험)
        if len(text) <= 15:
            return {"crisis": True, "level": "high"}
        else:
            return {"crisis": True, "level": "medium"}

    def get_response(self, level):
        """강도에 맞는 대응 메시지"""
        if level == "high":
            return (
                "지금 많이 힘드신 것 같아 걱정돼요. 혼자 견디지 않으셔도 돼요.\n"
                "24시간 언제든 전문 상담을 받을 수 있어요 — 자살예방상담 109번입니다.\n"
                "지금 바로 연락해 보시겠어요? 저도 여기 있을게요."
            )
        elif level == "medium":
            return (
                "요즘 정말 많이 지치고 힘드셨나 봐요. 그런 마음이 드는 게 이상한 게 아니에요.\n"
                "어떤 일들이 있었는지 편하게 들려주실래요? 제가 들을게요."
            )
        else:
            return None  # 위기 아님


# 테스트
gate = CrisisGate()

tests = [
    "오늘 날씨가 좋네요",              # 위기 아님
    "죽고 싶어",                       # 짧음 → 고위험
    "요즘 사는 게 너무 힘들고 자꾸 살기 싫다는 생각이 들어요",  # 긺 → 중위험
    "오늘 죽으려고 방법도 준비했어",   # 임박 → 고위험
]

for t in tests:
    result = gate.check(t)
    print(f"입력: {t}")
    print(f"판단: {result}")
    if result["crisis"]:
        print(f"응답: {gate.get_response(result['level'])}")
    print("-" * 40)