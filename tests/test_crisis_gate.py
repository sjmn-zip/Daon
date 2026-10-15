"""위기 탐지 게이트(CrisisGate) 단위 테스트 (Safety-First 검증)

Notion 트러블슈팅 이력 및 미탐 방지 원칙(미탐 > 오탐)에 기반한 핵심 안전망 테스트 케이스입니다.
"""

import pytest
from app.core.crisis_gate import CrisisGate

@pytest.fixture
def gate():
    return CrisisGate()

class TestCrisisGateNormalCases:
    """정상 일상 대화 테스트 (위기 신호 없음)"""

    @pytest.mark.parametrize("text", [
        "오늘 날씨가 정말 화창해서 기분이 좋아.",
        "점심에 맛있는 파스타 먹고 커피 마셨어.",
        "요즘 취업 준비 때문에 조금 스트레스 받네.",
        "면접 결과가 아직 안 나와서 조금 초조해.",
        "친구랑 사소한 일로 다퉈서 마음이 안 좋아."
    ])
    def test_normal_messages_not_flagged(self, gate, text):
        result = gate.check(text)
        assert result["crisis"] is False
        assert result["level"] is None
        assert len(result["matched_keywords"]) == 0

class TestCrisisGateHighImminent:
    """급성/임박 위기 신호 테스트 (high 등급 판정)"""

    @pytest.mark.parametrize("text", [
        "죽고 싶어",
        "살기 싫다",
        "사라지고 싶다",
        "더는 못 버티겠어",
        "오늘 죽으려고 방법도 준비했어",  # 09/01 트러블슈팅 미탐 버그 재현 및 방지 테스트
        "지금 옥상인데 끝내고 싶어",
        "약 먹고 세상을 떠나려구",
        "유서 써두고 더 못 버티겠어서 연락해"
    ])
    def test_imminent_crisis_flagged_high(self, gate, text):
        result = gate.check(text)
        assert result["crisis"] is True
        assert result["level"] == "high"
        assert len(result["matched_keywords"]) > 0

    def test_high_crisis_response_contains_emergency_hotline(self, gate):
        """고위험 감지 시 즉각 109 자살예방상담전화 번호 제공 여부 검증"""
        response = gate.get_response("high")
        assert "109" in response
        assert "1577-0199" in response
        assert "혼자 짊어지지 않으셔도" in response

class TestCrisisGateMediumCrisis:
    """장문 심리적 위기 토로 테스트 (medium 등급 판정)"""

    @pytest.mark.parametrize("text", [
        "남들은 다 잘나가는 것 같은데 나만 매일 뒤처지고 제자리걸음이라 세상을 떠나고 싶은 마음이 자꾸만 들어서 너무 답답해.",
        "아침에 일어날 때마다 눈을 안 떴으면 좋겠다는 생각이 들고 하루하루 버티는 게 너무 지옥 같아서 끝내고 싶다는 생각을 종종 해."
    ])
    def test_medium_crisis_flagged_medium(self, gate, text):
        result = gate.check(text)
        assert result["crisis"] is True
        assert result["level"] == "medium"
        assert len(result["matched_keywords"]) > 0

    def test_medium_crisis_response_focuses_on_listening(self, gate):
        """중위험 감지 시 일방적 차단 대신 경청 및 열린 질문 제공 검증"""
        response = gate.get_response("medium")
        assert "털어놓아 주실 수 있나요" in response
        assert "제가 온전히 들을게요" in response
        # 즉각적인 109 강제 주입 대신 경청 중심
        assert "109" not in response
