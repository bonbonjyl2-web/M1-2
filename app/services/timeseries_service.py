# app/services/timeseries_service.py

from app.schemas.timeseries_schema import TimeSeriesCreate
from app.utils.timeseries_utils import calculate_summary # 아까 만든 유틸 함수
from datetime import datetime

class TimeSeriesService:
    def __init__(self, repo):
        # 나중에 FirestoreRepository 등을 여기서 주입받습니다.
        self.repo = repo

    async def process_and_save(self, schema_data: TimeSeriesCreate):
        # 1. Pydantic 모델을 딕셔너리로 변환
        data_dict = schema_data.model_dump()

        # 2. [추가 로직] Utils에 있는 함수로 요약 계산
        # 예: 데이터 리스트에서 평균/최대/최소 계산
        summary = calculate_summary(schema_data.data)
        data_dict['summary'] = summary

        # 3. 가공 시간 추가
        data_dict['processed_at'] = datetime.now().isoformat()

        # 4. Repository를 통해 DB(Firestore)에 저장

        result = await self.repo.save_data(data_dict) 
        return result