from google import genai
from app.core.config import settings

class ChatService:
    def __init__(self):
        self.client = genai.Client(api_key=settings.GEMINI_API_KEY) if settings.GEMINI_API_KEY else None
        self.model = 'gemini-2.0-flash'

    async def generate_chat_response(self, user_message: str) -> str:
        try:
            # K-Beauty 전문가 페르소나 부여
            prompt = f"당신은 K-Beauty 전문가입니다. 한국 화장품과 피부 관리에 대해 친절하게 조언해 주세요. 답변은 한국어로 하세요.\n\n질문: {user_message}"
            
            if self.client is None:
                return "Gemini API 키가 설정되지 않았습니다."

            # 답변 생성
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            return response.text
        
        except Exception as e:
            print(f"❌ Gemini API 오류 발생: {e}")
            return "죄송합니다. 답변을 생성하는 중에 문제가 발생했어요."

chat_service = ChatService()