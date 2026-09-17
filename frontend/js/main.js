// 현재 브라우저 주소를 자동으로 사용
const API_BASE_URL = window.location.origin;

// 차트 객체를 저장할 변수 (중복 생성 방지용)
let trendChart = null;

// 1. 사용자 ID 가져오기
function getUserId() {
    const userIdInput = document.getElementById('userIdInput');
    return userIdInput && userIdInput.value.trim() !== "" ? userIdInput.value.trim() : "test_user_123";
}

// 2. 채팅 메시지 추가
function addMessage(text, sender) {
    const chatWindow = document.getElementById('chat-window');
    if (!chatWindow) return;
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', sender);
    msgDiv.innerText = text;
    chatWindow.appendChild(msgDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

// 3. AI 채팅 전송
async function sendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value.trim();
    if (!message) return;
    addMessage(message, 'user');
    input.value = '';
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/chat/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });
        const data = await response.json();
        addMessage(data.response, 'ai');
    } catch (error) {
        addMessage("❌ 서버 연결에 실패했습니다.", 'ai');
    }
}

// 4. [핵심] 데이터 로드 (요약 수치 + 차트 데이터)
async function loadTrends() {
    const currentUserId = getUserId();
    
    // 하단 리포트 엘리먼트
    const statAvg = document.getElementById('stat-avg');
    const statMax = document.getElementById('stat-max');
    const statMin = document.getElementById('stat-min');
    const statCount = document.getElementById('stat-count');
    const trendSummary = document.getElementById('trend-summary');

    try {
        // (A) 요약 데이터 가져오기 (하단 리포트용)
        const summaryRes = await fetch(`${API_BASE_URL}/api/v1/timeseries/trends/summary/${currentUserId}`);
        if (summaryRes.ok) {
            const s = await summaryRes.json();
            if (statAvg) statAvg.innerText = s.average;
            if (statMax) statMax.innerText = s.max_value;
            if (statMin) statMin.innerText = s.min_value;
            if (statCount) statCount.innerText = `${s.count}개`;
            if (trendSummary) trendSummary.innerHTML = `<p style="text-align:center; color:var(--primary);">👤 <b>${s.user_id}</b> 님 분석 완료</p>`;
        }

        // (B) 전체 데이터 가져오기 (차트 그리기용)
        const chartRes = await fetch(`${API_BASE_URL}/api/v1/timeseries/trends/chart/${currentUserId}`);
        if (chartRes.ok) {
            const chartData = await chartRes.json();
            if (chartData && chartData.length > 0) {
                renderChart(chartData); // 차트 그리기 함수 호출
            }
        }
    } catch (error) {
        console.error("데이터 로드 실패:", error);
        if (trendSummary) trendSummary.innerHTML = `<p>데이터가 없습니다. [샘플 데이터 생성]을 눌러주세요.</p>`;
    }
}

// 5. [핵심] Chart.js로 차트 그리기
function renderChart(data) {
    const canvas = document.getElementById('trendChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // 기존 차트가 있으면 삭제하고 새로 그림
    if (trendChart) {
        trendChart.destroy();
    }

    // 날짜순 정렬
    data.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

    trendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d.timestamp.split('T')[0]), // X축: 날짜
            datasets: [{
                label: '트렌드 지수',
                data: data.map(d => d.value), // Y축: 수치
                borderColor: '#ff7eb9',
                backgroundColor: 'rgba(255, 126, 185, 0.1)',
                fill: true,
                tension: 0.3, // 부드러운 곡선
                borderWidth: 2,
                pointRadius: 0 // 점 숨기기
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { maxTicksLimit: 8 }, grid: { display: false } },
                y: { beginAtZero: false }
            }
        }
    });
}

// 6. 샘플 데이터 생성
async function seedData() {
    const currentUserId = getUserId();
    if(!confirm(`[${currentUserId}] 사용자로 105개의 데이터를 생성할까요?`)) return;

    addMessage("데이터를 생성 중입니다...", 'ai');

    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/timeseries/trends/seed/${currentUserId}`, {
            method: 'POST'
        });
        if (response.ok) {
            alert("✅ 데이터 생성 완료!");
            loadTrends(); // 생성 후 즉시 차트와 리포트 갱신
        }
    } catch (error) {
        alert("데이터 생성 실패");
    }
}

// main.js 내부
async function fetchKeywordAnalysis() {

    const currentUserId = getUserId();

    const keywordsArea = document.getElementById('keywords-area');
    const summaryArea = document.getElementById('summary-area');

    try {
        
        const response = await fetch(`${API_BASE_URL}/api/v1/nlp/extract-nouns/${currentUserId}`, {
            method: 'POST', // 데이터 조회는 보통 GET을 사용합니다. (POST가 필요하다면 유지)
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) {
            const errorText = await response.text(); // 에러 내용 확인
            console.error("서버 응답 오류:", errorText);
            throw new Error("서버 응답 오류");
        }

        const data = await response.json();

        // 데이터가 정상적으로 들어오는지 확인
        console.log("받은 데이터:", data);

        // 1. 키워드 뱃지 렌더링
        keywordsArea.innerHTML = data.keywords.map(k => 
            `<span class="keyword-badge">#${k}</span>`
        ).join('');

        // 2. 요약 텍스트 업데이트
        summaryArea.innerText = data.summary;

    } catch (error) {
        console.error("키워드 분석 에러:", error);
        summaryArea.innerText = "분석 데이터를 불러오는 중 오류가 발생했습니다.";
    }
}

// 초기화
document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('user-input')?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
    document.getElementById('userIdInput')?.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') loadTrends();
    });
    
    loadTrends(); // 페이지 열자마자 데이터 로드 시도
    fetchKeywordAnalysis();

});