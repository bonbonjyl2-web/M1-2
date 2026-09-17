# app/routers/timeseries_router.py
from fastapi import APIRouter, HTTPException
from app.services.timeseries_service import timeseries_service
from app.schemas.timeseries_schema import TimeSeriesSummary
from app.services.timeseries_service import TimeSeriesService


router = APIRouter(prefix="/trends", tags=["Trends"])
timeseries_service = TimeSeriesService() # 여기서 인스턴스를 생성해야 합니다.

@router.post("/seed/{user_id}")
async def seed_data(user_id: str):
    # ⭐ 앞에 await를 반드시 붙여야 합니다!
    result = await timeseries_service.seed_kbeauty_data(user_id)
    return result

@router.get("/summary/{user_id}", response_model=TimeSeriesSummary)
async def get_trend_summary(user_id: str, metric_name: str = "k_beauty_trend_index"):
    # ⭐ 여기도 await가 필요합니다!
    summary = await timeseries_service.get_summary(user_id, metric_name)
    
    if not summary:
        raise HTTPException(status_code=404, detail="데이터를 찾을 수 없습니다.")
    return summary

@router.get("/chart/{user_id}")  # 이 부분이 없어서 404가 났던 것입니다!
async def get_trends(user_id: str):
    # 서비스에서 해당 유저의 모든 시계열 데이터를 가져오는 함수를 호출합니다.
    # (timeseries_service에 get_all_trends 함수가 있다고 가정)
    result = await timeseries_service.get_all_trends(user_id)
    if not result:
        raise HTTPException(status_code=404, detail="데이터가 없습니다. 먼저 생성을 눌러주세요.")
    return result