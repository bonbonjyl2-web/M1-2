import time
import feedparser
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# 1. Firebase Admin SDK 초기화 (서비스 계정 키 파일 경로 필요)
# 기존 프로젝트에 firebase 설정이 있다면 해당 모듈을 import해서 쓰셔도 됩니다.
if not firebase_admin._apps:
    cred = credentials.Certificate("serviceAccountKey.json") # 키 파일 경로 확인 필요
    firebase_admin.initialize_app(cred)

db = firestore.client()

def fetch_google_news(keyword="K-Beauty"):
    rss_url = f"https://news.google.com/rss/search?q={keyword}&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(rss_url)
    
    news_items = []
    for entry in feed.entries[:10]: # 상위 10개 수집
        news_items.append({
            "title": entry.title,
            "link": entry.link,
            "published": entry.get("published", ""),
            "collected_at": datetime.now(),
            "category": "K-Beauty"
        })
    return news_items

def save_to_firestore(news_items):
    # 'articles' 컬렉션에 데이터 저장
    for item in news_items:
        # URL을 인코딩하거나 변환하여 문서 ID로 사용 (중복 저장 방지)
        doc_id = item["link"].replace("/", "_").replace(":", "_")
        doc_ref = db.collection("articles").document(doc_id)
        
        # merge=True: 이미 존재하는 기사면 덮어쓰기/갱신
        doc_ref.set(item, merge=True)

if __name__ == "__main__":
    print("Firestore용 K-Beauty 뉴스 수집 파이프라인 시작...")
    
    while True:
        try:
            items = fetch_google_news(keyword="K-Beauty")
            save_to_firestore(items)
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] K-Beauty 뉴스 {len(items)}건 Firestore 저장 완료")
        except Exception as e:
            print(f"오류 발생: {e}")
            
        time.sleep(60) # RSS는 10초보다 1분(60초) 이상 간격 추천