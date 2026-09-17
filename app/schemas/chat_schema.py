from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str  # 사용자가 보낸 질문

class ChatResponse(BaseModel):
    response: str # AI가 답변한 내용