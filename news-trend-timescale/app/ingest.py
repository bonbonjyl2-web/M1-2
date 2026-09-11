import time
import psycopg2
import feedparser
from datetime import datetime

# DB 연결 정보
DB_HOST = "localhost"  # 로컬에서 실행 시 localhost
DB_PORT = "5432"
DB_NAME = "news_db"
DB_USER = "postgres"
DB_PASS = "postgres"   # 변경하신 비밀번호가 있다면 수정해 주세요

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

def fetch_google_news(keyword="인공지능"):
    # 구글 뉴스 RSS URL (한글 검색)
    rss_url = f"https://news.google.com/rss/search?q={keyword}&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(rss_url)
    
    news_items = []
    for entry in feed.entries[:5]:  # 상위 5개 기사 수집
        title = entry.title
        link = entry.link
        # 발행 시간을 현재 시간(UTC/KST)으로 기록
        published_at = datetime.utcnow()
        news_items.append((published_at, title, link))
    
    return news_items

def save_to_db(news_items):
    conn = get_db_connection()
    cur = conn.cursor()
    
    insert_query = """
    INSERT INTO news (time, title, url)
    VALUES (%s, %s, %s)
    """
    
    for item in news_items:
        cur.execute(insert_query, item)
        
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    print("실제 구글 뉴스 수집 파이프라인 시작...")
    
    # 10초마다 구글 뉴스를 수집하여 DB에 적재
    while True:
        try:
            items = fetch_google_news(keyword="IT")
            save_to_db(items)
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 구글 뉴스 {len(items)}건 수집 및 DB 저장 완료")
        except Exception as e:
            print(f"오류 발생: {e}")
            
        time.sleep(10)