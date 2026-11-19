import json
from google.cloud import firestore
from google.oauth2 import service_account 
from app.core.config import settings
from typing import List
from pathlib import Path

class FirestoreRepository:
    def __init__(self):
        self.collection_name = "trends"
        self.db = None

        try:
            if settings.FIRESTORE_CREDENTIALS_JSON:
                service_account_info = json.loads(settings.FIRESTORE_CREDENTIALS_JSON)
                credentials = service_account.Credentials.from_service_account_info(
                    service_account_info
                )
            else:
                current_file = Path(__file__).resolve()
                base_dir = current_file.parent.parent.parent
                key_path = base_dir / settings.GOOGLE_APPLICATION_CREDENTIALS

                if not key_path.exists():
                    print("Firestore credentials are not configured; database-dependent endpoints will be unavailable")
                    return

                credentials = service_account.Credentials.from_service_account_file(
                    str(key_path)
                )

            self.db = firestore.Client(project=settings.FIRESTORE_PROJECT_ID, credentials=credentials)
            print("✅ Firestore 연결 성공!")
        except Exception as e:
            print(f"❌ Firestore 초기화 실패: {e}")

    def _require_db(self):
        if self.db is None:
            raise RuntimeError("Firestore credentials are not configured")

    def save_timeseries_data(self, user_id: str, data: dict) -> str:
        """서비스에서 dict로 변환된 데이터를 받아 저장합니다."""
        self._require_db()
        # 데이터에 user_id 추가
        data["user_id"] = user_id
        
        # Firestore 저장
        doc_ref = self.db.collection(self.collection_name).document()
        doc_ref.set(data)
        return doc_ref.id

    def get_user_data(self, user_id: str) -> List[dict]:
        """특정 사용자의 데이터를 가져옵니다."""
        self._require_db()
        # .order_by("timestamp")를 쓰려면 인덱스 설정이 필요하므로 우선 빼고 테스트하세요.
        docs = self.db.collection(self.collection_name)\
                      .where("user_id", "==", user_id)\
                      .stream()
        return [doc.to_dict() for doc in docs]

    async def get_all_by_user(self, user_id: str):
        self._require_db()
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