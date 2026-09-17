from collections import Counter
from konlpy.tag import Okt # 형태소 분석기
from app.repositories.firestore_repository import firestore_repo

class NLPService:
    def __init__(self):
        self.okt = Okt()

    async def analyze_kbeauty_trends(self, user_id: str):
        data_list = await firestore_repo.get_all_by_user(user_id)

        if not data_list:
            return {"keywords": ["데이터 없음"], "summary": "먼저 데이터를 생성해주세요."}

        # 1. 모든 content 문장을 하나로 합치거나 리스트로 추출
        # 명사만 추출하여 리스트에 담기
        all_nouns = []
        for item in data_list:
            content = item.get("content", "")
            if content:
                # 명사만 추출 (Okt 사용)
                nouns = self.okt.nouns(content)
                all_nouns.extend(nouns)

        if not all_nouns:
            return {"keywords": ["분석 결과 없음"], "summary": "분석할 명사가 충분하지 않습니다."}

        # 2. 빈도수 계산
        word_counts = Counter(all_nouns)
        # 상위 5개 키워드 추출
        top_keywords = [item[0] for item in word_counts.most_common(5)]
        
        # 3. 요약 문구 생성
        summary = f"최근 트렌드 분석 결과, '{top_keywords[0]}' 관련 키워드가 가장 많이 언급되었습니다. '{', '.join(top_keywords[:2])}' 중심의 마케팅 전략을 추천합니다."
        
        return {
            "keywords": top_keywords,
            "summary": summary
        }
nlp_service = NLPService()