from fastapi import APIRouter, HTTPException
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.services.chat_service import chat_service

# 이 'router' 변수가 main.py의 app.include_router(chat_router.router, ...)와 연결됩니다.
router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest):
    """
    사용자의 메시지를 받아 Gemini AI의 답변을 반환합니다.
    """
    if not request.message:
        raise HTTPException(status_code=400, detail="메시지를 입력해주세요.")
    
    # 서비스 계층의 함수 호출
    ai_answer = await chat_service.generate_chat_response(request.message)
    
    return ChatResponse(response=ai_answer)