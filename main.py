from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.routers import chat_router, timeseries_router , nlp_router
from pydantic import BaseModel
from konlpy.tag import Okt

app = FastAPI(title=settings.PROJECT_NAME)

okt = Okt()

class TextRequest(BaseModel):
    text: str

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 곳에서 접속 허용 (테스트용)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(chat_router.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(timeseries_router.router, prefix="/api/v1/timeseries", tags=["timeseries"])
app.include_router(nlp_router.router, prefix="/api/v1/nlp", tags=["nlp"])

# -------------------------------------------------------------------
# 2. 기존 @app.get("/") 부분은 삭제하거나 주석 처리해야 합니다.
# 삭제하지 않으면 index.html 대신 JSON 메시지가 먼저 뜹니다.
# -------------------------------------------------------------------

# 3. 프론트엔드 정적 파일 연결 (맨 아래에 추가)
# 이 설정이 frontend 폴더 안의 index.html을 기본 화면으로 띄워줍니다.
@app.get("/")
def read_root():
    return {"message": "FastAPI backend is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)