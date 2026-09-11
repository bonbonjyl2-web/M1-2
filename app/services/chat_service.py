import os
import google.generativeai as genai
from dotenv import load_dotenv

# .env 파일에서 API 키 로드
load_dotenv()

# Gemini 설정
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# 모델 설정
model = genai.GenerativeModel('gemini-1.5-flash')

async def generate_chat_response(user_message):
    """
    사용자의 질문에 대해 Gemini API를 사용하여 답변을 생성합니다.
    """
    try:
        # K-Beauty 전문가 페르소나 부여
        prompt = f"당신은 K-Beauty 전문가입니다. 한국 화장품과 피부 관리에 대해 친절하게 조언해 주세요. 답변은 한국어로 하세요.\n\n질문: {user_message}"
        
        # 답변 생성
        response = model.generate_content(prompt)
        
        return response.text
    
    except Exception as e:
        print(f"Gemini API 오류 발생: {e}")
        return "죄송합니다. 답변을 생성하는 중에 문제가 발생했어요."

# --- 테스트 코드 ---
if __name__ == "__main__":
    import asyncio

    async def test_run():
        print("\n🚀 Gemini 기반 K-Beauty 챗봇 테스트 시작!")
        # API 키가 잘 로드되었는지 확인
        if not GEMINI_API_KEY:
            print("❌ 오류: .env 파일에 GEMINI_API_KEY가 설정되지 않았습니다.")
            return
            
        test_message = "한국에서 요즘 유행하는 스킨케어 루틴 알려줘!"
        result = await generate_chat_response(test_message)
        print(f"\n질문: {test_message}")
        print(f"답변: {result}")

    asyncio.run(test_run())