# M1-2
AI Agent 개발: 나만의 AI 비서 구축
# RSS 뉴스 기반 K-뷰티 트렌드 AI 비서

## 1. 서비스 소개
RSS 뉴스 데이터를 기반으로 K-뷰티 트렌드를 시계열로 분석하고,
GPT를 활용해 시장조사 요약과 마케팅 제안을 제공하는 AI 비서 서비스입니다.

## 2. 기술 스택
- Backend: Python, FastAPI, Firebase Firestore, OpenAI API
- Frontend: HTML, CSS, JavaScript
- Deploy: Render, Vercel

## 3. 주요 기능
- K-뷰티 뉴스 데이터 CRUD
- 시계열 데이터 요약
- GPT 기반 마케팅 제안 생성
- 대화 기록 저장 및 불러오기

## 4. 배포 URL
- Frontend: 
- Backend API:
- Swagger:

## 5. 로컬 실행 방법

### Backend
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload