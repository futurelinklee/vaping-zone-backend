# 베이핑존 리뷰 자동 생성기 API v2.1

상품 관리 및 리뷰 자동 생성을 위한 백엔드 API

## 🚀 주요 기능

- ✅ 상품 추가/수정/삭제
- ✅ 카테고리 관리 (기타/일회용/액상)
- ✅ 리뷰 자동 생성 (40-50자 템플릿)
- ✅ 엑셀 다운로드
- ✅ Cloudflare Workers 연동 지원

## 📦 배포 방법

### Render 배포

1. GitHub 저장소 연결
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `gunicorn app:app`
4. 자동 배포

### 환경 변수

- `PORT`: 자동 설정 (Render)

## 🔗 API 엔드포인트

- `GET /api/products/<channel>` - 상품 목록
- `POST /api/products/<channel>` - 상품 추가
- `PUT /api/products/<channel>/<product_no>` - 상품 수정
- `DELETE /api/products/<channel>/<product_no>` - 상품 삭제
- `POST /api/generate-reviews` - 리뷰 생성

## 📱 채널

- `vapingzone` - 베이핑존
- `juiceon` - 쥬스온
- `kukdae` - 국대쥬스
