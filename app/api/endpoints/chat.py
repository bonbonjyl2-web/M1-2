from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from app.core.config import settings

router = APIRouter()

# 제미나이 AI 설정
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

class ChatMessage(BaseModel):
    message: str

@router.post("/chat")
async def chat(chat_message: ChatMessage):
    try:
        response = model.generate_content(
            f"너는 K-Beauty 전문가야. 한국 화장품과 뷰티에 대해 친절하게 답변해줘. 질문: {chat_message.message}"
        )
        return {"reply": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))