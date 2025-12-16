# 베이핑존 리뷰 자동 생성기 - Backend API

Flask 기반 REST API 서버

## 기능

- 🛒 **베이핑존** (155개 상품)
- 🧃 **쥬스온** (134개 상품)  
- 🥤 **국대쥬스** (75개 상품)

## API Endpoints

### 1. 상품 로드
```
GET /api/load-products?channel={cafe24|juiceon|kukdae}
```

### 2. 리뷰 생성
```
POST /api/generate-reviews
Content-Type: application/json

{
  "products": [...],
  "count": 10,
  "api_key": "sk-...",
  "channel": "cafe24"
}
```

### 3. 엑셀 다운로드
```
GET /api/download-excel?channel={cafe24|juiceon|kukdae}
```

### 4. 헬스체크
```
GET /health
```

## 로컬 실행

```bash
pip install -r requirements.txt
python app.py
```

서버가 `http://localhost:5000` 에서 실행됩니다.

## 배포

### Railway
1. Railway 계정 생성
2. GitHub 저장소 연결
3. 자동 배포

### Render
1. Render 계정 생성
2. New Web Service
3. GitHub 저장소 연결
4. Start Command: `python app.py`

## 환경 변수

- `PORT`: 서버 포트 (기본값: 5000)
- `OPENAI_API_KEY`: OpenAI API 키 (선택사항, 클라이언트에서 전달 가능)

## 기술 스택

- Python 3.11+
- Flask 3.0.0
- OpenAI GPT-4o-mini
- openpyxl (Excel 처리)

## 라이센스

MIT
