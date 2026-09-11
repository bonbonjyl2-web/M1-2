import psycopg2
from collections import Counter

# DB 연결 정보
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "news_db"
DB_USER = "postgres"
DB_PASS = "postgres"

def analyze_keywords():
    # 1. DB 연결
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS
    )
    cursor = conn.cursor()

    # 2. 최근 저장된 뉴스 제목 100개 조회
    cursor.execute("SELECT title FROM news ORDER BY time DESC LIMIT 100;")
    rows = cursor.fetchall()

    if not rows:
        print("분석할 뉴스 데이터가 없습니다.")
        return

    # 3. 텍스트 분할 및 키워드 추출 (2글자 이상 단어 대상)
    words = []
    for row in rows:
        title = row[0]
        # 공백 기준으로 단어를 나누고 불필요한 조사/부호 간단 제거
        tokens = title.split()
        for token in tokens:
            cleaned_token = token.strip("[],.()\"'")
            if len(cleaned_token) >= 2:
                words.append(cleaned_token)

    # 4. 단어 빈도수 집계
    keyword_counts = Counter(words)

    # 5. 상위 5개 주요 키워드 출력
    print("\n[최근 뉴스 트렌드 키워드 TOP 5]")
    print("-" * 35)
    for rank, (word, count) in enumerate(keyword_counts.most_common(5), 1):
        print(f"{rank}위: {word:<15} ({count}회 등장)")
    print("-" * 35)

    cursor.close()
    conn.close()

if __name__ == "__main__":
    analyze_keywords()
