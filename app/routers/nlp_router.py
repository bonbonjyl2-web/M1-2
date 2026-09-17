from fastapi import APIRouter, HTTPException
from app.services.nlp_service import nlp_service
from app.schemas.nlp_schema import NLPAnalysisResponse

router = APIRouter()

@router.post("/extract-nouns/{user_id}", response_model=NLPAnalysisResponse)
async def extract_nouns(user_id: str):
    try:
        # nlp_service에서 명사 추출 로직 실행
        result = await nlp_service.analyze_kbeauty_trends(user_id)
        return result
    except Exception as e:
        # 에러 발생 시 500 에러와 함께 메시지 전송
        raise HTTPException(status_code=500, detail=str(e))