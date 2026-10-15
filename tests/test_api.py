"""FastAPI REST API 엔드포인트 통합 테스트"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    return TestClient(app)

class TestSystemEndpoints:
    def test_root_endpoint(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["project"] == "Daon (다온)"
        assert "/docs" in data["docs"]

    def test_health_endpoint(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["engine_ready"] is True

class TestChatEndpoints:
    def test_empty_message_validation_error(self, client):
        """빈 메시지 요청 시 Pydantic 검증 422 에러 반환 검증"""
        response = client.post("/api/v1/chat", json={"message": ""})
        assert response.status_code == 422

    def test_crisis_message_handled_by_crisis_gate(self, client):
        """위기 메시지 입력 시 LLM 호출 없이 게이트에서 즉각 안전 대응 반환 검증"""
        payload = {
            "message": "오늘 죽으려고 방법도 준비했어",
            "chat_history": []
        }
        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["is_crisis"] is True
        assert data["crisis_level"] == "high"
        assert data["source"] == "crisis_gate"
        assert "109" in data["response"]
