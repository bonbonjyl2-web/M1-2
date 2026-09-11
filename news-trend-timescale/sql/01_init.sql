-- TimescaleDB 확장 기능 활성화
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- 뉴스 데이터 테이블 생성
CREATE TABLE IF NOT EXISTS news (
    time TIMESTAMPTZ NOT NULL,
    id SERIAL,
    title TEXT NOT NULL,
    url TEXT,
    PRIMARY KEY (time, id)
);

-- TimescaleDB 하이퍼테이블로 변환
SELECT create_hypertable('news', 'time', if_not_exists => TRUE);
