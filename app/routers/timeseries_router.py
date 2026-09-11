from fastapi import APIRouter
from schemas.timeseries_schema import TimeSeriesCreate, TimeSeriesResponse
from services.timeseries_service import TimeSeriesService


router = APIRouter(prefix="/timeseries", tags=["TimeSeries"])
service = TimeSeriesService()


@router.post("/analyze", response_model=TimeSeriesResponse) # response_model은 유지!)
async def analyze_data(payload: TimeSeriesCreate):
    # 실제 복잡한 로직은 서비스에게 맡깁니다.
    result = await timeseries_service.process_timeseries_data(payload)
    return result