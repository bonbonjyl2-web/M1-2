import { useEffect, useMemo, useState } from 'react'
import './App.css'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''
const DEFAULT_USER_ID = 'user_123'
const SETTINGS_KEY = 'kbeauty-dashboard-settings'

function getSavedSettings() {
  const saved = window.localStorage.getItem(SETTINGS_KEY)

  if (!saved) {
    return { baseUrl: API_BASE_URL, userId: DEFAULT_USER_ID }
  }

  try {
    const parsed = JSON.parse(saved)
    return {
      baseUrl:
        (typeof parsed.baseUrl === 'string' ? parsed.baseUrl : API_BASE_URL)
          .trim()
          .replace(/\/+$/, ''),
      userId: typeof parsed.userId === 'string' ? parsed.userId : DEFAULT_USER_ID,
    }
  } catch {
    return { baseUrl: API_BASE_URL, userId: DEFAULT_USER_ID }
  }
}

async function requestJson(url, options) {
  const response = await fetch(url, options)
  const body = await response.text()
  let data

  try {
    data = body ? JSON.parse(body) : null
  } catch {
    data = body
  }

  if (!response.ok) {
    const detail =
      typeof data === 'object' && data !== null
        ? data.detail || data.message
        : data
    throw new Error(
      typeof detail === 'string' && detail
        ? `${detail} (HTTP ${response.status})`
        : `요청에 실패했습니다. (HTTP ${response.status})`,
    )
  }

  return data
}

function formatNumber(value) {
  return new Intl.NumberFormat('ko-KR', {
    maximumFractionDigits: 1,
  }).format(value)
}

function formatDate(value) {
  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return '날짜 미상'
  }

  return new Intl.DateTimeFormat('ko-KR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(date)
}

function TrendChart({ points }) {
  const chartPoints = useMemo(() => {
    return points
      .filter(
        (point) =>
          Number.isFinite(Number(point.value)) &&
          point.timestamp &&
          !Number.isNaN(new Date(point.timestamp).getTime()),
      )
      .sort(
        (left, right) =>
          new Date(left.timestamp).getTime() - new Date(right.timestamp).getTime(),
      )
      .slice(-30)
  }, [points])

  if (!chartPoints.length) {
    return (
      <div className="empty-chart">
        <span className="empty-chart-mark" aria-hidden="true">✳</span>
        <p>표시할 트렌드 데이터가 없습니다.</p>
      </div>
    )
  }

  const values = chartPoints.map((point) => Number(point.value))
  const min = Math.min(...values)
  const max = Math.max(...values)
  const range = max - min || 1
  const chartCoordinates = chartPoints.map((point, index) => ({
    x: chartPoints.length === 1 ? 350 : 30 + (index / (chartPoints.length - 1)) * 640,
    y: 180 - ((Number(point.value) - min) / range) * 145,
    value: Number(point.value),
    timestamp: point.timestamp,
  }))
  const line = chartCoordinates
    .map(({ x, y }) => `${x},${y}`)
    .join(' ')
  const area = `30,190 ${line} 670,190`

  return (
    <div className="chart-wrap">
      <svg
        className="trend-chart"
        viewBox="0 0 700 220"
        role="img"
        aria-label="최근 트렌드 지수 변화 그래프"
        preserveAspectRatio="none"
      >
        {[35, 83, 132, 180].map((y) => (
          <line
            key={y}
            x1="30"
            y1={y}
            x2="670"
            y2={y}
            className="chart-grid"
          />
        ))}
        <polygon points={area} className="chart-area" />
        <polyline points={line} className="chart-line" />
        {chartCoordinates.map((point) => (
          <circle
            key={`${point.timestamp}-${point.x}`}
            cx={point.x}
            cy={point.y}
            r="3.5"
            className="chart-dot"
          >
            <title>
              {formatDate(point.timestamp)} · {formatNumber(point.value)}
            </title>
          </circle>
        ))}
      </svg>
      <div className="chart-axis">
        <span>{formatDate(chartPoints[0].timestamp)}</span>
        <span>최근 30개 데이터</span>
        <span>{formatDate(chartPoints[chartPoints.length - 1].timestamp)}</span>
      </div>
    </div>
  )
}

function App() {
  const [settings, setSettings] = useState(getSavedSettings)
  const [baseUrlInput, setBaseUrlInput] = useState(settings.baseUrl)
  const [userIdInput, setUserIdInput] = useState(settings.userId)
  const [connection, setConnection] = useState(() =>
    settings.baseUrl ? settings : null,
  )
  const [connectionError, setConnectionError] = useState('')
  const [dashboard, setDashboard] = useState({
    points: [],
    summary: null,
  })
  const [dashboardState, setDashboardState] = useState(() =>
    settings.baseUrl ? 'loading' : 'idle',
  )
  const [dashboardError, setDashboardError] = useState('')
  const [refreshVersion, setRefreshVersion] = useState(0)
  const [isSeeding, setIsSeeding] = useState(false)
  const [chatInput, setChatInput] = useState('')
  const [chatMessages, setChatMessages] = useState([])
  const [isSending, setIsSending] = useState(false)
  const [chatError, setChatError] = useState('')

  useEffect(() => {
    if (!connection) {
      return
    }

    const controller = new AbortController()
    const encodedUserId = encodeURIComponent(connection.userId)
    const root = connection.baseUrl

    Promise.all([
      requestJson(
        `${root}/api/v1/timeseries/trends/chart/${encodedUserId}`,
        { signal: controller.signal },
      ),
      requestJson(
        `${root}/api/v1/timeseries/trends/summary/${encodedUserId}`,
        { signal: controller.signal },
      ),
    ])
      .then(([points, summary]) => {
        if (controller.signal.aborted) {
          return
        }

        if (!Array.isArray(points)) {
          throw new Error('차트 API가 배열 형식의 데이터를 반환하지 않았습니다.')
        }

        setDashboard({ points, summary })
        setDashboardState('success')
      })
      .catch((error) => {
        if (controller.signal.aborted) {
          return
        }

        setDashboard({ points: [], summary: null })
        setDashboardError(
          error instanceof Error ? error.message : '백엔드 요청에 실패했습니다.',
        )
        setDashboardState('error')
      })

    return () => controller.abort()
  }, [connection, refreshVersion])

  const latestPoint = useMemo(() => {
    return [...dashboard.points]
      .filter(
        (point) =>
          Number.isFinite(Number(point.value)) &&
          point.timestamp &&
          !Number.isNaN(new Date(point.timestamp).getTime()),
      )
      .sort(
        (left, right) =>
          new Date(right.timestamp).getTime() -
          new Date(left.timestamp).getTime(),
      )[0]
  }, [dashboard.points])

  const recentPoints = useMemo(() => {
    return [...dashboard.points]
      .filter((point) => point.timestamp)
      .sort(
        (left, right) =>
          new Date(right.timestamp).getTime() -
          new Date(left.timestamp).getTime(),
      )
      .slice(0, 5)
  }, [dashboard.points])

  function connectBackend(event) {
    event.preventDefault()
    setConnectionError('')

    const baseUrl = baseUrlInput.trim().replace(/\/+$/, '')
    const userId = userIdInput.trim()

    if (!baseUrl || !userId) {
      setConnectionError('백엔드 주소와 사용자 ID를 모두 입력해 주세요.')
      return
    }

    try {
      const parsedUrl = new URL(baseUrl)
      if (!['http:', 'https:'].includes(parsedUrl.protocol)) {
        throw new Error('백엔드 주소는 http 또는 https URL이어야 합니다.')
      }
    } catch (error) {
      setConnectionError(
        error instanceof Error && error.message.startsWith('백엔드 주소')
          ? error.message
          : '올바른 백엔드 주소를 입력해 주세요. 예: https://api.example.com',
      )
      return
    }

    const nextSettings = { baseUrl, userId }

    try {
      window.localStorage.setItem(SETTINGS_KEY, JSON.stringify(nextSettings))
    } catch {
      setConnectionError('브라우저에 연결 설정을 저장하지 못했습니다.')
      return
    }

    setSettings(nextSettings)
    setBaseUrlInput(baseUrl)
    setUserIdInput(userId)
    setDashboard({ points: [], summary: null })
    setDashboardState('loading')
    setDashboardError('')
    setConnection(nextSettings)
    setChatMessages([])
    setChatError('')
  }

  async function seedSampleData() {
    if (!connection) {
      return
    }

    setIsSeeding(true)
    setDashboardError('')

    try {
      const result = await requestJson(
        `${connection.baseUrl}/api/v1/timeseries/trends/seed/${encodeURIComponent(connection.userId)}`,
        { method: 'POST' },
      )

      if (result?.status === 'error') {
        throw new Error(result.message || '샘플 데이터를 생성하지 못했습니다.')
      }

      setDashboardState('loading')
      setRefreshVersion((version) => version + 1)
    } catch (error) {
      setDashboardError(
        error instanceof Error ? error.message : '샘플 데이터 생성에 실패했습니다.',
      )
    } finally {
      setIsSeeding(false)
    }
  }

  async function sendMessage(event) {
    event.preventDefault()
    const message = chatInput.trim()

    if (!connection || !message || isSending) {
      return
    }

    setChatInput('')
    setChatError('')
    setChatMessages((messages) => [...messages, { role: 'user', text: message }])
    setIsSending(true)

    try {
      const result = await requestJson(`${connection.baseUrl}/api/v1/chat/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message }),
      })

      if (typeof result?.response !== 'string') {
        throw new Error('채팅 API 응답 형식이 올바르지 않습니다.')
      }

      setChatMessages((messages) => [
        ...messages,
        { role: 'assistant', text: result.response },
      ])
    } catch (error) {
      setChatError(
        error instanceof Error ? error.message : '메시지를 전송하지 못했습니다.',
      )
    } finally {
      setIsSending(false)
    }
  }

  const isConnected = Boolean(connection)

  return (
    <main className="dashboard-shell">
      <header className="topbar">
        <a className="brand" href="/" aria-label="K-Beauty 인사이트 홈">
          <span className="brand-mark" aria-hidden="true">b.</span>
          <span>beau<span className="brand-accent">trend</span></span>
        </a>
        <div className="topbar-right">
          <span className={`connection-pill ${isConnected ? 'is-ready' : ''}`}>
            <span className="status-dot" />
            {isConnected ? '백엔드 연결 설정됨' : '연결 설정 필요'}
          </span>
          <a className="topbar-link" href="#settings">연결 설정</a>
        </div>
      </header>

      <section className="hero-section">
        <div className="hero-copy">
          <span className="eyebrow"><span /> BEAUTY, BACKED BY DATA</span>
          <h1>트렌드를 읽고,<br /><span>다음 기회를 발견하세요.</span></h1>
          <p>실시간 K-뷰티 인사이트를 한곳에서 확인하고 AI와 함께 다음 전략을 찾아보세요.</p>
        </div>
        <div className="hero-orbit" aria-hidden="true">
          <div className="orbit orbit-one" />
          <div className="orbit orbit-two" />
          <div className="orbit-center">뷰티<br />인사이트</div>
          <span className="orbit-sparkle sparkle-one">✳</span>
          <span className="orbit-sparkle sparkle-two">✦</span>
          <span className="orbit-sparkle sparkle-three">✧</span>
        </div>
      </section>

      <section className="settings-card" id="settings">
        <div className="settings-heading">
          <div>
            <span className="section-kicker">GET CONNECTED</span>
            <h2>내 백엔드 연결하기</h2>
          </div>
          <span className="settings-index">01 / CONNECT</span>
        </div>
        <form className="settings-form" onSubmit={connectBackend}>
          <label>
            <span>백엔드 주소</span>
            <input
              type="url"
              placeholder="https://your-api.example.com"
              value={baseUrlInput}
              onChange={(event) => setBaseUrlInput(event.target.value)}
              required
            />
          </label>
          <label>
            <span>사용자 ID</span>
            <input
              type="text"
              placeholder="user_123"
              value={userIdInput}
              onChange={(event) => setUserIdInput(event.target.value)}
              required
            />
          </label>
          <button className="button button-dark connect-button" type="submit">
            데이터 불러오기 <span aria-hidden="true">↗</span>
          </button>
        </form>
        <p className="settings-hint">
          주소는 FastAPI 서버의 기본 주소를 입력하세요. 사용자 ID는 백엔드에 저장된 데이터와 일치해야 합니다.
        </p>
        {connectionError && <p className="inline-error" role="alert">{connectionError}</p>}
      </section>

      <section className="overview-section" aria-labelledby="overview-title">
        <div className="section-heading">
          <div>
            <span className="section-kicker">YOUR BEAUTY BRIEFING</span>
            <h2 id="overview-title">오늘의 트렌드 브리핑</h2>
          </div>
          <div className="section-actions">
            {isConnected && (
              <button
                className="button button-outline"
                type="button"
                onClick={() => {
                  setDashboardState('loading')
                  setDashboardError('')
                  setRefreshVersion((version) => version + 1)
                }}
                disabled={dashboardState === 'loading'}
              >
                {dashboardState === 'loading' ? '불러오는 중…' : '새로고침 ↻'}
              </button>
            )}
          </div>
        </div>

        {!isConnected && (
          <div className="notice-card">
            <span className="notice-icon" aria-hidden="true">↗</span>
            <div>
              <strong>백엔드 주소를 연결하면 실제 데이터가 표시됩니다.</strong>
              <p>위 입력란에 배포된 FastAPI 서버 주소와 사용자 ID를 입력해 주세요.</p>
            </div>
          </div>
        )}

        {dashboardState === 'loading' && (
          <div className="notice-card loading-card" role="status">
            <span className="loading-spinner" />
            <div>
              <strong>백엔드 데이터를 불러오고 있어요.</strong>
              <p>Firestore 트렌드 기록을 확인하는 중입니다.</p>
            </div>
          </div>
        )}

        {dashboardState === 'error' && (
          <div className="notice-card error-card" role="alert">
            <span className="notice-icon" aria-hidden="true">!</span>
            <div>
              <strong>데이터를 불러오지 못했습니다.</strong>
              <p>{dashboardError}</p>
              <p className="error-hint">
                백엔드가 실행 중인지, 사용자 ID가 맞는지, 서버 CORS에서 이 Vercel 도메인을 허용하는지 확인해 주세요.
              </p>
              {dashboardError.includes('(HTTP 404)') && (
                <button
                  className="button button-dark seed-button"
                  type="button"
                  onClick={seedSampleData}
                  disabled={isSeeding}
                >
                  {isSeeding ? '샘플 생성 중…' : '이 사용자에게 샘플 데이터 105개 생성'}
                </button>
              )}
            </div>
          </div>
        )}

        {dashboardState === 'success' && (
          <>
            <div className="stats-grid">
              <article className="stat-card stat-primary">
                <div className="stat-topline">
                  <span>가장 최근 트렌드</span>
                  <span className="stat-icon">✳</span>
                </div>
                <strong>{latestPoint ? formatNumber(latestPoint.value) : '—'}</strong>
                <span className="stat-caption">
                  {latestPoint ? formatDate(latestPoint.timestamp) : '데이터 없음'}
                </span>
                <span className="stat-decoration" aria-hidden="true">✳</span>
              </article>
              <article className="stat-card">
                <div className="stat-topline">
                  <span>전체 평균</span>
                  <span className="stat-icon icon-lilac">↗</span>
                </div>
                <strong>
                  {dashboard.summary
                    ? formatNumber(dashboard.summary.average)
                    : '—'}
                </strong>
                <span className="stat-caption">트렌드 지수 평균</span>
              </article>
              <article className="stat-card">
                <div className="stat-topline">
                  <span>최고 트렌드 지수</span>
                  <span className="stat-icon icon-peach">↑</span>
                </div>
                <strong>
                  {dashboard.summary
                    ? formatNumber(dashboard.summary.max_value)
                    : '—'}
                </strong>
                <span className="stat-caption">기록된 최댓값</span>
              </article>
              <article className="stat-card">
                <div className="stat-topline">
                  <span>데이터 포인트</span>
                  <span className="stat-icon icon-green">◎</span>
                </div>
                <strong>
                  {dashboard.summary
                    ? formatNumber(dashboard.summary.count)
                    : formatNumber(dashboard.points.length)}
                </strong>
                <span className="stat-caption">수집된 전체 기록</span>
              </article>
            </div>

            <div className="content-grid">
              <article className="panel trend-panel">
                <div className="panel-heading">
                  <div>
                    <span className="section-kicker">TREND INDEX</span>
                    <h3>K-뷰티 트렌드 변화</h3>
                  </div>
                  <span className="panel-badge">최근 30개 기록</span>
                </div>
                <TrendChart points={dashboard.points} />
                <div className="chart-legend">
                  <span className="legend-dot" /> K-뷰티 트렌드 지수
                </div>
              </article>

              <article className="panel range-panel">
                <div className="panel-heading">
                  <div>
                    <span className="section-kicker">AT A GLANCE</span>
                    <h3>지수 범위</h3>
                  </div>
                  <span className="range-sparkle" aria-hidden="true">✳</span>
                </div>
                <div className="range-value">
                  <span>최고</span>
                  <strong>
                    {dashboard.summary
                      ? formatNumber(dashboard.summary.max_value)
                      : '—'}
                  </strong>
                </div>
                <div className="range-track"><span /></div>
                <div className="range-value range-low">
                  <span>최저</span>
                  <strong>
                    {dashboard.summary
                      ? formatNumber(dashboard.summary.min_value)
                      : '—'}
                  </strong>
                </div>
                <p className="range-footnote">
                  {dashboard.summary
                    ? `${dashboard.summary.metric_name} 기준`
                    : '트렌드 요약을 불러오지 못했습니다.'}
                </p>
              </article>
            </div>

            <article className="panel activity-panel">
              <div className="panel-heading">
                <div>
                  <span className="section-kicker">LATEST SIGNALS</span>
                  <h3>최근 트렌드 기록</h3>
                </div>
                <span className="activity-count">
                  {formatNumber(dashboard.points.length)}개 기록
                </span>
              </div>
              {recentPoints.length ? (
                <ul className="activity-list">
                  {recentPoints.map((point, index) => (
                    <li key={point.id || `${point.timestamp}-${index}`}>
                      <span className="activity-marker" aria-hidden="true">
                        {String(index + 1).padStart(2, '0')}
                      </span>
                      <div className="activity-copy">
                        <strong>{point.content || point.metric_name || '트렌드 데이터'}</strong>
                        <span>{formatDate(point.timestamp)}</span>
                      </div>
                      <span className="activity-value">
                        {Number.isFinite(Number(point.value))
                          ? formatNumber(point.value)
                          : '—'}
                      </span>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="activity-empty">아직 표시할 기록이 없습니다.</p>
              )}
            </article>
          </>
        )}
      </section>

      <section className="assistant-section" aria-labelledby="assistant-title">
        <div className="assistant-intro">
          <span className="section-kicker">YOUR AI BEAUTY PARTNER</span>
          <h2 id="assistant-title">인사이트를<br /><span>대화로 넓혀보세요.</span></h2>
          <p>뷰티 트렌드에 대해 궁금한 점을 물어보세요. K-뷰티 전문가 AI가 한국어로 답변합니다.</p>
          <span className="assistant-flower" aria-hidden="true">✳</span>
        </div>
        <div className="chat-panel">
          <div className="chat-heading">
            <div className="chat-avatar">b.</div>
            <div>
              <strong>뷰티 인사이트 AI</strong>
              <span><i /> K-뷰티 전문가</span>
            </div>
            <span className="chat-sparkle" aria-hidden="true">✦</span>
          </div>
          <div className="chat-messages" aria-live="polite">
            {!chatMessages.length && (
              <div className="chat-welcome">
                <span aria-hidden="true">✳</span>
                <p>안녕하세요! K-뷰티 트렌드나 뷰티 전략에 대해 무엇이든 물어보세요.</p>
              </div>
            )}
            {chatMessages.map((message, index) => (
              <div
                className={`chat-message ${message.role === 'user' ? 'from-user' : 'from-assistant'}`}
                key={`${message.role}-${index}`}
              >
                {message.text}
              </div>
            ))}
            {isSending && <div className="chat-message from-assistant">답변을 준비하고 있어요…</div>}
            {chatError && <p className="chat-error" role="alert">{chatError}</p>}
          </div>
          <form className="chat-form" onSubmit={sendMessage}>
            <input
              type="text"
              aria-label="AI에게 보낼 메시지"
              placeholder={isConnected ? '궁금한 트렌드를 물어보세요…' : '먼저 백엔드 주소를 연결해 주세요'}
              value={chatInput}
              onChange={(event) => setChatInput(event.target.value)}
              disabled={!isConnected || isSending}
            />
            <button
              type="submit"
              aria-label="메시지 보내기"
              disabled={!isConnected || isSending || !chatInput.trim()}
            >
              ↗
            </button>
          </form>
        </div>
      </section>

      <footer className="footer">
        <a className="brand footer-brand" href="/" aria-label="K-Beauty 인사이트 홈">
          <span className="brand-mark" aria-hidden="true">b.</span>
          <span>beau<span className="brand-accent">trend</span></span>
        </a>
        <span>작은 신호에서, 다음 뷰티 트렌드까지.</span>
        <span>© 2026 BEAUTREND</span>
      </footer>
      <span className="connection-description" aria-live="polite">
        {isConnected ? `연결된 사용자: ${settings.userId}` : ''}
      </span>
    </main>
  )
}

export default App
