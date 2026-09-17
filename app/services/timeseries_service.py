import os
import random
from datetime import datetime, timedelta
from app.repositories.firestore_repository import firestore_repo
from app.schemas.timeseries_schema import TimeSeriesBase, TimeSeriesSummary


class TimeSeriesService:
    async def seed_kbeauty_data(self, user_id: str):
            base_date = datetime.now()
            # 분석을 위한 샘플 뉴스 문장 리스트
            news_samples = [
        "비건 화장품 시장이 급성장하며 친환경 성분이 주목받고 있습니다.",
        "K-뷰티의 핵심은 이제 맞춤형 피부 진단 서비스입니다.",
        "환절기 피부 보습을 위한 세라마이드 성분 제품이 인기입니다.",
        "글로벌 시장에서 K-뷰티 선케어 제품의 수요가 폭발적입니다.",
        "천연 유래 성분을 강조한 클린 뷰티가 트렌드를 주도합니다."
        ]
            
            try:
                # --- 1. Firestore 데이터 생성 (105개) ---
                for i in range(105):
                    random_content = random.choice(news_samples)
            
                    sample_data = TimeSeriesBase(
                        timestamp=base_date - timedelta(days=i),
                        value=float(random.randint(50, 100)),
                        metric_name="k_beauty_trend_index",
                        content=random_content  # [추가] 분석용 텍스트 필드
                    )
                    
                    # Pydantic 모델을 dict로 변환
                    data_to_save = sample_data.dict() 
                    
                    # [수정] firestore_repo.save_timeseries_data는 일반 함수이므로 await 없이 호출
                    firestore_repo.save_timeseries_data(user_id, data_to_save)
    
                # --- 2. 뉴스 샘플 파일 생성 (생략 - 기존 코드와 동일) ---
                # ... (파일 생성 로직)
    
                print(f"✅ {user_id} 데이터 저장 완료!")
                return {"status": "success", "message": "데이터 생성 완료"}
    
            except Exception as e:
                print(f"❌ 서비스 에러 발생: {e}") # 터미널에 에러가 찍히게 함
                return {"status": "error", "message": str(e)}

    async def get_summary(self, user_id: str, metric_name: str = "k_beauty_trend_index") -> TimeSeriesSummary:
        """
        Firestore에서 데이터를 가져와 평균, 최대, 최소, 개수를 분석합니다.
        """
        raw_data = firestore_repo.get_user_data(user_id)
        
        # 해당 metric_name만 필터링
        filtered_values = [d['value'] for d in raw_data if d.get('metric_name') == metric_name]

        if not filtered_values:
            return None

        return TimeSeriesSummary(
            user_id=user_id,
            metric_name=metric_name,
            average=round(sum(filtered_values) / len(filtered_values), 2),
            max_value=max(filtered_values),
            min_value=min(filtered_values),
            count=len(filtered_values)
        )
    
    async def get_all_trends(self, user_id: str):
    # 리포지토리에서 데이터를 가져와서 그대로 반환
        return await firestore_repo.get_all_by_user(user_id)

# 서비스 인스턴스 생성
timeseries_service = TimeSeriesService()