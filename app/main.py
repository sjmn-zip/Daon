"""Daon (다온) FastAPI Backend Application

Safety-First 멘탈케어 챗봇 코어 엔진을 서빙하는 REST API 서버입니다.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(
    title="🌿 Daon (다온) API",
    description="감정 분류기와 위기 탐지 게이트를 결합한 Safety-First 멘탈케어 대화형 챗봇 REST API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정 (향후 Phase 8~9 React / Web 프론트엔드 연동 대비)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 단계 전체 허용, 프로덕션 전환 시 특정 도메인 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(router)

@app.get("/", tags=["System"])
def root():
    return {
        "project": "Daon (다온)",
        "description": "Safety-First 멘탈케어 챗봇 REST API 서버",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
