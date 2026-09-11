WITH a AS (
    INSERT INTO articles (
        source,
        title,
        url,
        content,
        sentiment,
        published_at
    )
    VALUES
    (
        'Yonhap',
        'AI 반도체 시장 급성장',
        'https://example.com/news/1',
        'AI 반도체 수요가 빠르게 증가하고 있다.',
        0.75,
        now() - INTERVAL '3 hours'
    )
    RETURNING id, published_at
)
INSERT INTO topic_mentions (article_id, keyword, score, published_at)
SELECT id, 'AI', 3, published_at FROM a
UNION ALL
SELECT id, '반도체', 2, published_at FROM a;

WITH a AS (
    INSERT INTO articles (
        source,
        title,
        url,
        content,
        sentiment,
        published_at
    )
    VALUES
    (
        'KBS',
        '금리 동결에 시장 안정세',
        'https://example.com/news/2',
        '기준금리 동결 이후 증시가 안정세를 보였다.',
        0.20,
        now() - INTERVAL '2 hours'
    )
    RETURNING id, published_at
)
INSERT INTO topic_mentions (article_id, keyword, score, published_at)
SELECT id, '금리', 3, published_at FROM a
UNION ALL
SELECT id, '증시', 2, published_at FROM a;

WITH a AS (
    INSERT INTO articles (
        source,
        title,
        url,
        content,
        sentiment,
        published_at
    )
    VALUES
    (
        'BBC',
        'Global AI regulation debate expands',
        'https://example.com/news/3',
        'Governments are discussing AI regulation.',
        0.10,
        now() - INTERVAL '1 hour'
    )
    RETURNING id, published_at
)
INSERT INTO topic_mentions (article_id, keyword, score, published_at)
SELECT id, 'AI', 3, published_at FROM a
UNION ALL
SELECT id, '규제', 2, published_at FROM a;

-- continuous aggregate 초기 갱신
CALL refresh_continuous_aggregate(
    'keyword_trend_1h',
    now() - INTERVAL '30 days',
    now()
);