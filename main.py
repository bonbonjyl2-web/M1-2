from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import chat, timeseries  # 분리된 라우터들 임포트

app = FastAPI(title=settings.PROJECT_NAME)

# 1. CORS 설정 (프론트엔드 연결 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. 라우터 등록 (기능 연결)
# 챗봇 기능 연결
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])
# 시계열 분석 기능 연결
app.include_router(timeseries.router, prefix="/api/v1/timeseries", tags=["timeseries"])

@app.get("/")
def read_root():
    return {"message": "K-Beauty AI Server is running!"}

if __name__ == "__main__":
    import uvicorn
    # 서버 실행: 여기서 main은 파일명, app은 FastAPI 인스턴스 이름입니다.
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)