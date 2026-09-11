from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

# 1. 기본 데이터 포인트 (공통 속성)
class TimeSeriesBase(BaseModel):
    timestamp: datetime = Field(..., example="2023-10-27T10:00:00")
    value: float = Field(..., example=75.5)
    metric_name: str = Field(..., example="heart_rate")

# 2. 생성 요청 (Request): 클라이언트가 서버로 보낼 때
# 보통 시계열은 여러 데이터를 리스트로 묶어서 보냅니다.
class TimeSeriesCreate(BaseModel):
    user_id: str = Field(..., example="user_123")
    data: List[TimeSeriesBase] # 여러 개의 데이터 포인트를 한 번에 받음

# 3. 개별 데이터 응답 (Response): DB 저장 후 하나씩 보여줄 때
class TimeSeriesResponse(TimeSeriesBase):
    id: str = Field(..., description="Firestore 문서 ID")
    user_id: str

# 4. 요약 결과 응답 (Summary): 분석 결과를 보여줄 때 (4번 단계와 연결)
class TimeSeriesSummary(BaseModel):
    user_id: str
    metric_name: str
    average: float
    max_value: float
    min_value: float
    count: int