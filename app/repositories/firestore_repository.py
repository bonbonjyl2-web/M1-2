# app/repositories/firestore_repository.py
from google.cloud import firestore

class FirestoreRepository:
    def __init__(self):
        # 1. AsyncClient를 사용합니다.
        self.db = firestore.AsyncClient() 
        self.collection = self.db.collection("timeseries_data")

    # 2. 함수 앞에 'async'를 붙여줍니다.
    async def save_data(self, data: dict):
        doc_ref = self.collection.document()
        
        # 3. DB에 저장하는 동안 기다려야 하므로 'await'를 붙여줍니다.
        await doc_ref.set(data) 
        
        return {"id": doc_ref.id, **data}