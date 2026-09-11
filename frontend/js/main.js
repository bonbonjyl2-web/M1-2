// 1. HTML 요소 가져오기
const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

// 2. 화면에 메시지를 뿌려주는 함수
function addMessage(sender, text) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message');
    messageDiv.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
    messageDiv.innerText = text;
    chatMessages.appendChild(messageDiv);
    
    // 메시지가 많아지면 자동으로 아래로 스크롤
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 3. 백엔드(FastAPI)와 통신하는 함수
async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    // 사용자 메시지 화면 표시
    addMessage('user', message);
    userInput.value = '';

    try {
        // 백엔드 서버 주소 (8002번 포트 확인!)
        const response = await fetch('http://127.0.0.1:8002/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message }),
        });

        if (!response.ok) {
            throw new Error('서버 응답 오류');
        }

        const data = await response.json();
        // 챗봇 답변 화면 표시
        addMessage('bot', data.reply);

    } catch (error) {
        console.error('Error:', error);
        addMessage('bot', '서버와 연결할 수 없습니다. 백엔드가 8002 포트에서 실행 중인지 확인하세요.');
    }
}

// 4. 클릭 및 엔터키 이벤트 리스너
sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});