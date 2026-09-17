from google.cloud import firestore
from google.oauth2 import service_account 
from app.core.config import settings
from typing import List
from pathlib import Path

class FirestoreRepository:
    def __init__(self):
        # 1. 컬렉션 이름 반드시 정의!
        self.collection_name = "trends"
        
        current_file = Path(__file__).resolve()
        base_dir = current_file.parent.parent.parent
        key_path = base_dir / settings.GOOGLE_APPLICATION_CREDENTIALS
        
        if not key_path.exists():
            raise FileNotFoundError(f"Key file not found at {key_path}")

        try:
            credentials = service_account.Credentials.from_service_account_file(str(key_path))
            self.db = firestore.Client(project=settings.FIRESTORE_PROJECT_ID, credentials=credentials)
            print(f"✅ Firestore 연결 성공!")
        except Exception as e:
            print(f"❌ Firestore 초기화 실패: {e}")
            raise e

    def save_timeseries_data(self, user_id: str, data: dict) -> str:
        """서비스에서 dict로 변환된 데이터를 받아 저장합니다."""
        # 데이터에 user_id 추가
        data["user_id"] = user_id
        
        # Firestore 저장
        doc_ref = self.db.collection(self.collection_name).document()
        doc_ref.set(data)
        return doc_ref.id

    def get_user_data(self, user_id: str) -> List[dict]:
        """특정 사용자의 데이터를 가져옵니다."""
        # .order_by("timestamp")를 쓰려면 인덱스 설정이 필요하므로 우선 빼고 테스트하세요.
        docs = self.db.collection(self.collection_name)\
                      .where("user_id", "==", user_id)\
                      .stream()
        return [doc.to_dict() for doc in docs]

    async def get_all_by_user(self, user_id: str):
    # 1. 특정 유저의 timeseries 컬렉션에 접근
        docs = self.db.collection(self.collection_name)\
                      .where("user_id", "==", user_id)\
                      .stream()
    
        results = []
        for doc in docs:
            results.append(doc.to_dict())
    
    # 2. 시간순(timestamp)으로 정렬해서 반환
        results.sort(key=lambda x: x.get('timestamp', ''))
        return results

firestore_repo = FirestoreRepository()