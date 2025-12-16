#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
카페24 리뷰 자동 생성 스크립트 V2
실제 업로드 양식 기반
"""

import openpyxl
from datetime import datetime, timedelta
import random
import json
import sys

# 종류별 리뷰 템플릿
REVIEW_TEMPLATES = {
    "액상": [
        "기대했던 맛 이상으로 괜찮았어요",
        "목넘김이 부드럽고 맛이 좋네요",
        "향이 진하지 않아서 좋아요",
        "재구매 의사 100% 입니다",
        "가격 대비 만족스러워요",
        "처음 써봤는데 생각보다 좋네요",
        "은은한 향이 마음에 들어요",
        "다른 제품보다 훨씬 나아요",
        "맛이 깔끔하고 좋습니다",
        "추천받아서 구매했는데 만족해요",
        "리필용으로 계속 구매할게요",
        "향도 좋고 가격도 착해요",
        "생각했던 것보다 더 좋아요",
        "입문자에게 딱 좋은 제품이에요",
        "배송도 빠르고 품질도 좋아요",
        "친구한테도 추천했어요",
        "기대 이상입니다 만족해요",
        "자극적이지 않아서 좋네요",
        "부드러운 맛이 일품이에요",
        "재구매 했습니다 역시 좋아요"
    ],
    "기기": [
        "누수없고 디자인도 깔끔해서 만족합니다",
        "휴대성 좋고 사용하기 편해요",
        "배터리 오래가서 좋습니다",
        "디자인 예쁘고 성능 좋아요",
        "입문자에게 추천합니다",
        "가성비 최고예요 강추합니다",
        "심플한 디자인이 마음에 들어요",
        "품질 좋고 사용감도 만족스러워요",
        "생각보다 훨씬 좋네요",
        "충전도 빠르고 오래가요",
        "크기도 적당하고 좋습니다",
        "처음 사용해봤는데 만족해요",
        "가볍고 휴대하기 편해요",
        "디자인 깔끔하고 성능도 좋아요",
        "사용법도 간단하고 좋습니다",
        "배송 빠르고 제품도 만족스러워요",
        "가격 대비 훌륭한 제품이에요",
        "재구매 의사 있습니다",
        "친구 선물용으로도 좋을 것 같아요",
        "기대했던 것보다 더 좋아요"
    ],
    "일회용": [
        "휴대하기 편하고 맛도 좋아요",
        "간편하게 사용할 수 있어서 좋네요",
        "맛이 진하고 만족스러워요",
        "가격 대비 괜찮은 제품입니다",
        "처음 사용해봤는데 생각보다 좋아요",
        "출장용으로 딱이에요",
        "목넘김 부드럽고 좋습니다",
        "간단하게 사용하기 좋아요",
        "휴대성이 최고예요",
        "여행갈 때 유용하게 쓸 것 같아요",
        "은은한 맛이 마음에 듭니다",
        "재구매 의향 있어요",
        "편리하고 맛도 좋네요",
        "간편하게 즐기기 좋아요",
        "가볍고 사용하기 편해요",
        "디자인도 예쁘고 좋습니다",
        "배송 빠르고 제품 만족해요",
        "친구 추천으로 구매했는데 좋네요",
        "생각보다 오래가서 좋아요",
        "기대 이상이에요 만족합니다"
    ]
}

# 작성자 이름 풀
REVIEWER_NAMES = [
    "김**", "이**", "박**", "최**", "정**",
    "강**", "조**", "윤**", "장**", "임**",
    "한**", "오**", "서**", "신**", "권**",
    "황**", "안**", "송**", "전**", "홍**",
    "구매자***", "만족한고객**", "재구매의향**", "vape***",
    "happy***", "user***", "good***", "nice***"
]

def generate_random_datetime(days_back=3):
    """랜덤 날짜/시간 생성 (당일~3일 전)"""
    now = datetime.now()
    random_days = random.randint(0, days_back)
    random_hours = random.randint(0, 23)
    random_minutes = random.randint(0, 59)
    random_seconds = random.randint(0, 59)
    
    random_date = now - timedelta(days=random_days)
    random_date = random_date.replace(
        hour=random_hours,
        minute=random_minutes,
        second=random_seconds
    )
    
    return random_date.strftime("%Y-%m-%d %H:%M:%S")

def detect_category(product_type):
    """종류에서 카테고리 감지"""
    product_type_lower = product_type.lower()
    
    if "일회용" in product_type:
        return "일회용"
    elif "기기" in product_type or "킷" in product_type:
        return "기기"
    elif "액상" in product_type:
        return "액상"
    else:
        # 기본값은 액상
        return "액상"

def generate_reviews(products, review_count):
    """
    리뷰 생성
    :param products: [{"product_no": "11", "type": "미션 기기", "name": "미션 전자담배 킷 - 넵튠블루"}, ...]
    :param review_count: 생성할 총 리뷰 개수
    :return: 리뷰 데이터 리스트
    """
    reviews = []
    
    # 각 제품에 리뷰를 랜덤 분산
    for i in range(review_count):
        # 랜덤으로 제품 선택
        product = random.choice(products)
        
        # 종류에서 카테고리 감지
        category = detect_category(product.get("type", ""))
        
        # 카테고리에 맞는 리뷰 템플릿 선택
        template_list = REVIEW_TEMPLATES.get(category, REVIEW_TEMPLATES["액상"])
        review_content = random.choice(template_list)
        
        # 리뷰 데이터 생성
        review = {
            "product_no": product["product_no"],
            "product_code": "",  # 비워둠
            "option": "",  # 상품 옵션 비워둠
            "date": generate_random_datetime(),
            "author": random.choice(REVIEWER_NAMES),
            "rating": 5,  # 항상 5점
            "title": "",  # 미입력 시 내용이 제목으로
            "content": review_content,
            "image1": "",
            "image2": "",
            "image3": "",
            "image4": ""
        }
        
        reviews.append(review)
    
    return reviews

def create_excel(reviews, output_path):
    """
    엑셀 파일 생성 (카페24 양식)
    :param reviews: 리뷰 데이터 리스트
    :param output_path: 저장할 파일 경로
    """
    # 새 워크북 생성
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    
    # 헤더 작성
    headers = [
        "product_no", "product_code", "상품 옵션", "작성일",
        "작성자", "별점", "제목", "내용",
        "이미지 URL 1", "이미지 URL 2", "이미지 URL 3", "이미지 URL 4"
    ]
    
    for col_idx, header in enumerate(headers, 1):
        ws.cell(row=1, column=col_idx, value=header)
    
    # 리뷰 데이터 작성
    for row_idx, review in enumerate(reviews, 2):
        ws.cell(row=row_idx, column=1, value=review["product_no"])
        ws.cell(row=row_idx, column=2, value=review["product_code"])
        ws.cell(row=row_idx, column=3, value=review["option"])
        ws.cell(row=row_idx, column=4, value=review["date"])
        ws.cell(row=row_idx, column=5, value=review["author"])
        ws.cell(row=row_idx, column=6, value=review["rating"])
        ws.cell(row=row_idx, column=7, value=review["title"])
        ws.cell(row=row_idx, column=8, value=review["content"])
        ws.cell(row=row_idx, column=9, value=review["image1"])
        ws.cell(row=row_idx, column=10, value=review["image2"])
        ws.cell(row=row_idx, column=11, value=review["image3"])
        ws.cell(row=row_idx, column=12, value=review["image4"])
    
    # 파일 저장
    wb.save(output_path)
    return output_path

def main():
    """메인 함수 - CLI에서 JSON 입력 받기"""
    if len(sys.argv) < 2:
        print("Usage: python generate_reviews_v2.py '<JSON_DATA>'")
        sys.exit(1)
    
    try:
        # JSON 파라미터 파싱
        data = json.loads(sys.argv[1])
        products = data.get("products", [])
        review_count = data.get("count", 10)
        output_path = data.get("output", "cafe24_reviews.xlsx")
        
        if not products:
            print("Error: No products provided")
            sys.exit(1)
        
        # 리뷰 생성
        reviews = generate_reviews(products, review_count)
        
        # 엑셀 파일 생성
        output_file = create_excel(reviews, output_path)
        
        # 성공 메시지 (JSON 형식)
        result = {
            "success": True,
            "file": output_file,
            "review_count": len(reviews),
            "message": f"{len(reviews)}개의 리뷰가 생성되었습니다."
        }
        print(json.dumps(result, ensure_ascii=False))
        
    except Exception as e:
        # 에러 메시지 (JSON 형식)
        result = {
            "success": False,
            "error": str(e)
        }
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(1)

if __name__ == "__main__":
    main()
