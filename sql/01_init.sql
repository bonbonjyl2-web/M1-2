CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 뉴스 기사 원본 테이블
CREATE TABLE IF NOT EXISTS articles (
    id BIGSERIAL,
    source TEXT NOT NULL,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    content TEXT,
    sentiment NUMERIC(5, 2),
    published_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now(),

    PRIMARY KEY (id, published_at),
    UNIQUE (url, published_at)
);

-- articles 테이블을 시계열 최적화 테이블로 변환
SELECT create_hypertable(
    'articles',
    'published_at',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- 뉴스에서 추출한 키워드 등장 정보
CREATE TABLE IF NOT EXISTS topic_mentions (
    article_id BIGINT NOT NULL,
    keyword TEXT NOT NULL,
    score INTEGER DEFAULT 1,
    published_at TIMESTAMPTZ NOT NULL,

    PRIMARY KEY (article_id, keyword, published_at)
);

-- topic_mentions도 시계열 최적화
SELECT create_hypertable(
    'topic_mentions',
    'published_at',
    chunk_time_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- 최근 시간 기준 키워드 검색 최적화
CREATE INDEX IF NOT EXISTS idx_mentions_keyword_time
ON topic_mentions (keyword, published_at DESC);

-- 언론사별, 시간별 조회 최적화
CREATE INDEX IF NOT EXISTS idx_articles_source_time
ON articles (source, published_at DESC);

-- 1시간 단위 키워드 트렌드 집계
CREATE MATERIALIZED VIEW IF NOT EXISTS keyword_trend_1h
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', published_at) AS bucket,
    keyword,
    COUNT(*) AS mention_count,
    COUNT(DISTINCT article_id) AS article_count,
    AVG(score) AS avg_score
FROM topic_mentions
GROUP BY bucket, keyword
WITH NO DATA;

-- continuous aggregate 자동 갱신 정책
SELECT add_continuous_aggregate_policy(
    'keyword_trend_1h',
    start_offset => INTERVAL '7 days',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '15 minutes',
    if_not_exists => TRUE
);

-- 오래된 데이터 압축 정책
ALTER TABLE topic_mentions SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'keyword',
    timescaledb.compress_orderby = 'published_at DESC'
);

SELECT add_compression_policy(
    'topic_mentions',
    INTERVAL '7 days',
    if_not_exists => TRUE
);