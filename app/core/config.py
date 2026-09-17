import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

# 1. 최상위 루트 경로 설정 (app/core/config.py 기준 세 단계 위)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "K-Beauty Chatbot"
    
    # .env 파일에서 읽어올 변수들 (기본값 설정으로 에러 방지)
    FIRESTORE_PROJECT_ID: str = "k-beauty-intellegence-chat-bot"
    GEMINI_API_KEY: str = "" # .env에 없으면 빈 값
    
    # ⭐ 중요: 테스트 코드처럼 '전체 경로'를 만들어 줍니다.
    GOOGLE_APPLICATION_CREDENTIALS: str = str(BASE_DIR / "serviceAccountKey.json")

    # Pydantic 설정
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings()

# 서버 실행 시 터미널에서 경로가 맞는지 확인하기 위한 출력
print(f"🔍 설정 로드 중...")
print(f"📂 BASE_DIR: {BASE_DIR}")
print(f"🔑 키 파일 경로: {settings.GOOGLE_APPLICATION_CREDENTIALS}")
print(f"✅ 프로젝트 ID: {settings.FIRESTORE_PROJECT_ID}")