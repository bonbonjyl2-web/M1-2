import os
import random
from datetime import datetime, timedelta
from pathlib import Path
from google.cloud import firestore
from google.oauth2 import service_account

# 1. 경로 설정 (테스트 성공한 방식 그대로)
BASE_DIR = Path(__file__).resolve().parent
JSON_NAME = "serviceAccountKey.json"
key_path = BASE_DIR / JSON_NAME

def test_bulk_insert():
    if not key_path.exists():
        print(f"❌ 에러: {JSON_NAME} 파일이 없습니다!")
        return

    try:
        # 2. Firestore 연결
        credentials = service_account.Credentials.from_service_account_file(str(key_path))
        db = firestore.Client(project="k-beauty-intellegence-chat-bot", credentials=credentials)
        
        print("🚀 100개 데이터 생성을 시작합니다...")
        
        # 3. 샘플 데이터 준비 (K-뷰티 키워드)
        keywords = ["Glow Skin", "Vegan Beauty", "Cica Care", "Glass Skin", "Sun Serum"]
        categories = ["Skincare", "Makeup", "Eco-Friendly"]
        
        # Firestore Batch 사용 (한 번에 대량으로 넣을 때 효율적임)
        batch = db.batch()
        
        for i in range(100):
            # 랜덤 데이터 생성
            data = {
                "keyword": random.choice(keywords),
                "value": random.randint(10, 100),
                "timestamp": datetime.now() - timedelta(days=i), # 최근 100일 데이터
                "category": random.choice(categories),
                "region": "Global"
            }
            
            # 'trends' 컬렉션에 문서 생성
            doc_ref = db.collection("trends").document()
            batch.set(doc_ref, data)
            
            if (i + 1) % 20 == 0:
                print(f"📦 {i + 1}개 준비 완료...")

        # 4. 한꺼번에 커밋
        batch.commit()
        print("✅ 성공: 100개의 데이터가 'trends' 컬렉션에 저장되었습니다!")

    except Exception as e:
        print(f"❌ 실패: {e}")

if __name__ == "__main__":
    test_bulk_insert()