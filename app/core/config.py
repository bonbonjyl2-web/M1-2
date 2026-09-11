import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv

# 1. .env 파일 위치 찾기 (최상위 루트)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
env_path = os.path.join(BASE_DIR, ".env")

# 2. .env 파일 강제 로드
load_dotenv(env_path)

class Settings(BaseSettings):
    PROJECT_NAME: str = "K-Beauty Chatbot"
    
    # .env에서 읽어올 변수들 (기본값을 None으로 주어 에러 방지)
    FIRESTORE_PROJECT_ID: str = os.getenv("FIRESTORE_PROJECT_ID", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    model_config = SettingsConfigDict(
        extra='ignore'
    )

# 설정 객체 생성
settings = Settings()

# 확인용 출력
if __name__ == "__main__":
    print(f"--- 설정 로드 테스트 ---")
    print(f"경로: {env_path}")
    print(f"GEMINI_API_KEY 존재 여부: {'✅ 있음' if settings.GEMINI_API_KEY else '❌ 없음'}")
    print(f"FIRESTORE_ID 존재 여부: {'✅ 있음' if settings.FIRESTORE_PROJECT_ID else '❌ 없음'}")