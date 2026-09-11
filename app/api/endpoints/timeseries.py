from fastapi import APIRouter, HTTPException

from app.repositories.firestore_repository import FirestoreRepository
from app.schemas.timeseries_schema import TimeSeriesCreate, TimeSeriesResponse
from app.services.timeseries_service import TimeSeriesService


router = APIRouter()

# 의존성 주입 (Service와 Repository 연결)
repo = FirestoreRepository()
service = TimeSeriesService(repo)


@router.post("/analyze", response_model=TimeSeriesResponse)
async def analyze_timeseries(data: TimeSeriesCreate):
	try:
		# 서비스 호출
		result = await service.process_and_save(data)
		return result
	except Exception as e:
		raise HTTPException(status_code=500, detail=str(e))
