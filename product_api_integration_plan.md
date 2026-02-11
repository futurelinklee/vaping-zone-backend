# 상품 관리 기능 통합 계획

## 1. 백엔드 API 추가
파일: `app.py` 또는 별도 blueprint

```python
# 상품 조회
@app.route('/api/products/<channel>', methods=['GET'])

# 상품 추가  
@app.route('/api/products/<channel>', methods=['POST'])

# 상품 삭제
@app.route('/api/products/<channel>/<int:product_no>', methods=['DELETE'])

# 상품 목록 다운로드
@app.route('/api/products/<channel>/download', methods=['GET'])
```

## 2. 프론트엔드 추가
파일: `static/product_manager.html`

- 기존 리뷰 생성기와 동일한 스타일
- 3개 채널 탭 (베이핑존/쥬스온/국대쥬스)
- 메인 페이지에서 "상품 관리" 메뉴 링크

## 3. 데이터 파일
기존 파일 활용:
- `data/upload_template.xlsx` (베이핑존)
- `data/juiceon_template.xlsx` (쥬스온)
- `data/kukdae_template.xlsx` (국대쥬스)

## 4. 배포
- GitHub 푸시
- Render 자동 재배포
- 고정 주소 사용: https://vaping-zone-review-generator.futurelinklee.workers.dev/

## 5. 장점
✅ 고정 주소 (주소 변경 없음)
✅ 통합 관리 (리뷰 + 상품)
✅ 데이터 일관성
✅ 편리한 접근
