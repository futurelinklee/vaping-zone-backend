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

# 종류별 리뷰 템플릿 (길고 자연스럽게)
REVIEW_TEMPLATES = {
    "액상": [
        "처음 구매해봤는데 향도 좋고 목넘김도 부드러워서 정말 만족스럽습니다. 가격도 합리적이고 배송도 빨라서 좋았어요. 다음에도 또 구매할 생각입니다.",
        "리필용으로 구매했는데 역시 기대를 저버리지 않네요. 맛도 깔끔하고 질리지 않아서 계속 쓸 것 같아요. 주변 분들에게도 추천드립니다.",
        "친구 추천으로 구매했는데 생각보다 훨씬 좋습니다. 향이 은은하고 자극적이지 않아서 부담없이 사용하고 있어요. 재구매 의향 100%입니다.",
        "여러 제품 써봤지만 이게 제일 마음에 드네요. 목넘김이 부드럽고 맛도 오래 지속되는 것 같아요. 재구매 확정이고 주변에도 적극 추천하고 있습니다.",
        "가격 대비 정말 만족스러운 제품이에요. 향도 좋고 품질도 우수해서 다른 사람들에게도 추천하고 싶네요. 배송도 빠르고 포장도 꼼꼼했습니다.",
        "입문자인데 사용하기 편하고 맛도 좋아서 만족합니다. 처음 쓰는 분들한테 강력 추천드려요. 자극도 적당하고 향도 부드럽습니다.",
        "배송도 빠르고 제품 상태도 아주 좋았습니다. 맛이 깔끔하고 은은해서 질리지 않고 계속 쓸 수 있을 것 같아요. 가성비도 정말 훌륭한 제품입니다.",
        "기대했던 것보다 훨씬 더 좋네요. 향이 진하지 않아서 좋고 목넘김도 아주 부드러워요. 다음에 또 구매할게요. 정말 만족스럽습니다.",
        "여러모로 만족스러운 제품입니다. 품질도 좋고 가격도 착해서 부담없이 구매할 수 있어요. 처음 사용하시는 분들께도 추천합니다.",
        "리뷰 보고 반신반의하며 샀는데 정말 좋네요. 맛도 좋고 향도 은은해서 마음에 듭니다. 이 가격에 이 품질이면 정말 가성비 최고입니다.",
        "자극적이지 않고 부드러워서 정말 좋아요. 처음 써보시는 분들도 부담없이 사용하실 수 있을 것 같습니다. 향도 은은하고 목넘김도 부드럽습니다.",
        "재구매 여러 번 했는데 항상 만족스럽습니다. 품질이 일정하고 맛도 변함없이 좋아요. 앞으로도 계속 구매할 예정입니다.",
        "다른 제품들보다 훨씬 나은 것 같아요. 향도 좋고 목넘김도 부드러워서 계속 쓰고 있습니다. 주변 지인들에게도 적극 추천 중입니다.",
        "친구 선물로도 정말 좋을 것 같아요. 포장도 깔끔하고 제품 품질도 우수합니다. 받는 분도 분명 만족하실 거예요.",
        "가성비 최고의 제품이에요. 이 가격에 이 품질이면 정말 만족스럽습니다. 배송도 빠르고 포장도 안전하게 잘 왔어요.",
        "향이 너무 좋아서 계속 쓰게 되네요. 질리지 않는 맛이 정말 마음에 듭니다. 다른 제품도 궁금해서 다음엔 다른 것도 구매해볼 생각입니다.",
        "처음에는 의심했는데 써보니 정말 좋습니다. 목넘김 부드럽고 향도 은은해요. 가격도 합리적이고 품질도 우수합니다.",
        "배송 빠르고 포장 꼼꼼해서 좋았어요. 제품 자체도 만족스럽고 재구매 의향 충분히 있습니다. 주변에도 추천하고 있어요.",
        "여행용으로 샀는데 휴대하기도 편하고 맛도 정말 좋아서 만족합니다. 작은 사이즈라 가방에 넣고 다니기도 편하네요.",
        "품질 대비 가격이 정말 착한 것 같아요. 앞으로 계속 구매할 예정입니다. 향도 좋고 목넘김도 부드러워서 만족스럽습니다.",
        "오랜만에 정말 만족스러운 제품을 찾았어요. 향도 좋고 맛도 깔끔해서 질리지 않네요. 재구매 의사 200%입니다.",
        "주변 추천으로 처음 구매해봤는데 역시 괜찮네요. 목넘김도 부드럽고 향도 은은해서 부담 없이 즐길 수 있습니다.",
        "여러 제품 비교해보고 구매했는데 선택을 잘한 것 같아요. 가격도 착하고 품질도 우수합니다. 매우 만족스럽습니다.",
        "생각보다 훨씬 좋아서 깜짝 놀랐어요. 향도 진하지 않고 적당해서 좋고 목넘김도 아주 부드럽습니다. 강력 추천합니다.",
        "재구매 3번째인데 역시 실망시키지 않네요. 품질이 변함없이 우수하고 맛도 일정해서 믿고 삽니다. 앞으로도 계속 애용할게요."
    ],
    "기기": [
        "누수 전혀 없고 디자인도 깔끔해서 정말 만족합니다. 휴대하기도 편하고 성능도 우수해요. 입문자에게 강력 추천드립니다.",
        "휴대성 좋고 사용하기도 정말 편해요. 배터리도 오래가고 충전도 빠릅니다. 가격 대비 훌륭한 제품이에요.",
        "배터리가 정말 오래가서 좋습니다. 하루종일 사용해도 문제없고 디자인도 심플해서 마음에 듭니다. 재구매 의향 있어요.",
        "디자인 정말 예쁘고 성능도 아주 좋아요. 사용법도 간단해서 초보자도 쉽게 사용할 수 있습니다. 주변에도 추천하고 있어요.",
        "입문자에게 강력 추천합니다. 사용법도 간단하고 성능도 우수해요. 가격도 합리적이고 품질도 정말 좋습니다.",
        "가성비 최고예요 정말 강추합니다. 이 가격에 이런 품질이면 정말 만족스럽습니다. 배송도 빠르고 포장도 꼼꼼했어요.",
        "심플한 디자인이 정말 마음에 들어요. 휴대하기도 편하고 성능도 우수합니다. 처음 사용하시는 분들께도 추천드려요.",
        "품질 정말 좋고 사용감도 매우 만족스러워요. 배터리도 오래가고 충전도 빠릅니다. 재구매 의사 충분히 있습니다.",
        "생각보다 훨씬 좋네요. 디자인도 깔끔하고 성능도 우수합니다. 가격도 착해서 부담없이 구매했는데 정말 잘 샀어요.",
        "충전도 빠르고 배터리도 정말 오래가요. 하루종일 사용해도 문제없습니다. 휴대성도 좋고 디자인도 세련됐어요.",
        "크기도 적당하고 무게도 가벼워서 정말 좋습니다. 휴대하기 편하고 사용감도 우수해요. 주변에도 추천하고 있습니다.",
        "처음 사용해봤는데 정말 만족해요. 사용법도 간단하고 성능도 우수합니다. 입문자에게 딱 좋은 제품인 것 같아요.",
        "가볍고 휴대하기 정말 편해요. 디자인도 심플하고 성능도 좋습니다. 배터리도 오래가서 하루종일 사용 가능해요.",
        "디자인 깔끔하고 성능도 정말 좋아요. 사용법이 간단해서 초보자도 쉽게 사용할 수 있습니다. 가성비도 우수합니다.",
        "사용법도 간단하고 성능도 정말 좋습니다. 배터리 지속시간도 길고 충전도 빠릅니다. 매우 만족스러운 제품이에요.",
        "배송 빠르고 제품도 정말 만족스러워요. 디자인도 세련되고 성능도 우수합니다. 재구매 의향 충분히 있어요.",
        "가격 대비 정말 훌륭한 제품이에요. 품질도 우수하고 성능도 좋습니다. 주변 지인들에게도 적극 추천하고 있습니다.",
        "재구매 의사 충분히 있습니다. 품질도 우수하고 성능도 변함없이 좋아요. 앞으로도 계속 애용할 생각입니다.",
        "친구 선물용으로도 정말 좋을 것 같아요. 포장도 깔끔하고 디자인도 세련됐습니다. 받는 분도 분명 만족하실 거예요.",
        "기대했던 것보다 훨씬 더 좋아요. 디자인도 깔끔하고 성능도 우수합니다. 가격도 합리적이고 품질도 정말 좋습니다.",
        "오래 사용해도 성능 저하가 없어서 정말 좋아요. 내구성도 우수하고 디자인도 세련됐습니다. 매우 만족스러운 제품입니다.",
        "처음 입문하시는 분들에게 정말 추천드립니다. 사용법도 간단하고 성능도 우수해요. 가격도 착하고 품질도 좋습니다.",
        "여러 제품 비교해보고 구매했는데 선택을 잘한 것 같아요. 성능도 우수하고 디자인도 마음에 듭니다. 재구매 확정이에요.",
        "배터리 성능이 정말 우수합니다. 하루종일 사용해도 문제없고 충전도 빠릅니다. 휴대성도 좋고 디자인도 깔끔해요.",
        "재구매 2번째인데 역시 만족스럽네요. 품질이 변함없이 우수하고 성능도 일정합니다. 앞으로도 계속 애용할게요."
    ],
    "일회용": [
        "휴대하기 정말 편하고 맛도 아주 좋아요. 간편하게 사용할 수 있어서 출장이나 여행 갈 때 딱 좋습니다. 재구매 의향 있어요.",
        "간편하게 사용할 수 있어서 정말 좋네요. 맛도 깔끔하고 향도 은은해서 만족스럽습니다. 가격도 합리적이고 품질도 우수해요.",
        "맛이 진하고 정말 만족스러워요. 휴대하기도 편하고 디자인도 깔끔합니다. 출장용으로 구매했는데 아주 잘 사용하고 있어요.",
        "가격 대비 정말 괜찮은 제품입니다. 맛도 좋고 향도 은은해요. 간편하게 사용할 수 있어서 바쁜 일상에 딱 좋습니다.",
        "처음 사용해봤는데 생각보다 훨씬 좋아요. 목넘김도 부드럽고 맛도 깔끔합니다. 휴대성도 우수해서 만족스러워요.",
        "출장용으로 정말 딱이에요. 가볍고 휴대하기 편해서 가방에 넣고 다니기 좋습니다. 맛도 좋고 향도 은은해요.",
        "목넘김 부드럽고 정말 좋습니다. 맛도 깔끔하고 향도 적당해요. 간편하게 사용할 수 있어서 바쁠 때 유용합니다.",
        "간단하게 사용하기 정말 좋아요. 휴대성도 우수하고 맛도 만족스럽습니다. 가격도 합리적이고 품질도 좋아요.",
        "휴대성이 정말 최고예요. 작고 가벼워서 어디든 가지고 다니기 편합니다. 맛도 좋고 향도 은은해서 만족합니다.",
        "여행갈 때 유용하게 쓸 것 같아요. 휴대하기 편하고 맛도 깔끔합니다. 가격도 착하고 품질도 우수해요.",
        "은은한 맛이 정말 마음에 듭니다. 자극적이지 않고 부드러워서 좋아요. 간편하게 사용할 수 있어서 만족스럽습니다.",
        "재구매 의향 충분히 있어요. 맛도 좋고 휴대성도 우수합니다. 가격도 합리적이고 품질도 변함없이 좋아요.",
        "편리하고 맛도 정말 좋네요. 간편하게 사용할 수 있어서 바쁜 일상에 딱입니다. 휴대성도 우수하고 디자인도 깔끔해요.",
        "간편하게 즐기기 정말 좋아요. 맛도 깔끔하고 향도 은은합니다. 출장이나 여행용으로 구매하시면 만족하실 거예요.",
        "가볍고 사용하기 정말 편해요. 휴대성도 우수하고 맛도 만족스럽습니다. 가격도 착해서 부담없이 구매할 수 있어요.",
        "디자인도 예쁘고 성능도 정말 좋습니다. 맛도 깔끔하고 향도 은은해요. 휴대하기 편해서 어디든 가지고 다닙니다.",
        "배송 빠르고 제품도 정말 만족해요. 맛도 좋고 휴대성도 우수합니다. 재구매 의향 충분히 있는 제품이에요.",
        "친구 추천으로 구매했는데 정말 좋네요. 맛도 깔끔하고 향도 은은합니다. 간편하게 사용할 수 있어서 만족스럽습니다.",
        "생각보다 오래가서 정말 좋아요. 맛도 변함없이 유지되고 향도 일정합니다. 가성비도 우수한 제품이에요.",
        "기대 이상이에요 정말 만족합니다. 맛도 좋고 휴대성도 우수해요. 가격도 합리적이고 품질도 변함없이 좋습니다.",
        "간편하게 사용할 수 있어서 바쁜 일상에 딱입니다. 맛도 깔끔하고 향도 은은해요. 주변에도 추천하고 있어요.",
        "여러 제품 써봤지만 이게 제일 마음에 드네요. 맛도 좋고 휴대성도 우수합니다. 재구매 확정이에요.",
        "출장 많은 직장인에게 정말 추천드립니다. 휴대하기 편하고 맛도 깔끔해요. 간편하게 사용할 수 있어서 유용합니다.",
        "처음 구매했는데 역시 좋네요. 맛도 깔끔하고 향도 은은합니다. 휴대성도 우수하고 가격도 합리적이에요.",
        "재구매 여러 번 했는데 항상 만족스럽습니다. 품질이 일정하고 맛도 변함없이 좋아요. 앞으로도 계속 구매할게요."
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

# 카테고리별 제목 템플릿
TITLE_TEMPLATES = {
    "액상": [
        "만족스러운 제품이에요",
        "재구매 의향 100%",
        "기대 이상입니다",
        "향이 정말 좋아요",
        "목넘김 부드럽네요",
        "가성비 최고",
        "품질 우수합니다",
        "강력 추천드려요",
        "정말 만족합니다",
        "다음에 또 구매할게요",
        "생각보다 훨씬 좋아요",
        "맛이 깔끔해요",
        "은은한 향이 좋네요",
        "부드럽고 좋습니다",
        "재구매 확정이에요",
        "추천합니다",
        "만족스럽네요",
        "좋은 제품이에요",
        "품질 좋아요",
        "가격도 착해요"
    ],
    "기기": [
        "디자인 깔끔해요",
        "성능 좋습니다",
        "휴대하기 편해요",
        "배터리 오래가요",
        "사용하기 편리해요",
        "가성비 좋네요",
        "입문자에게 추천",
        "만족스러운 구매",
        "품질 우수해요",
        "재구매 의향 있어요",
        "충전 빠르고 좋아요",
        "심플하고 좋습니다",
        "크기 적당해요",
        "가볍고 좋네요",
        "사용감 만족",
        "추천드려요",
        "괜찮은 제품",
        "마음에 들어요",
        "성능 만족",
        "좋은 선택이었어요"
    ],
    "일회용": [
        "간편하고 좋아요",
        "휴대성 최고",
        "맛 좋습니다",
        "편리해요",
        "출장용으로 딱",
        "여행용 추천",
        "만족스러워요",
        "가성비 좋네요",
        "간단하게 좋아요",
        "재구매 의향",
        "목넘김 부드러워요",
        "은은한 맛",
        "디자인 예뻐요",
        "사용 편해요",
        "오래가요",
        "추천합니다",
        "괜찮은 제품",
        "만족해요",
        "좋은 선택",
        "품질 좋아요"
    ]
}

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
    
    # 중복 방지를 위한 세트
    used_reviews = set()
    used_names = set()
    
    # 각 제품에 리뷰를 랜덤 분산
    for i in range(review_count):
        # 랜덤으로 제품 선택
        product = random.choice(products)
        
        # 종류에서 카테고리 감지
        category = detect_category(product.get("type", ""))
        
        # 카테고리에 맞는 리뷰 템플릿 선택 (중복 방지)
        template_list = REVIEW_TEMPLATES.get(category, REVIEW_TEMPLATES["액상"])
        review_content = None
        for attempt in range(50):
            temp_review = random.choice(template_list)
            if temp_review not in used_reviews:
                review_content = temp_review
                used_reviews.add(review_content)
                break
        
        # 중복을 피할 수 없으면 약간 변형
        if review_content is None:
            review_content = random.choice(template_list)
            suffix = random.choice(['', ' ', '!', '~'])
            review_content = review_content + suffix
            used_reviews.add(review_content)
        
        # 제목 생성 (카테고리별 템플릿 사용)
        title_list = TITLE_TEMPLATES.get(category, TITLE_TEMPLATES["액상"])
        review_title = random.choice(title_list)
        
        # 작성자 이름 선택 (중복 방지)
        author_name = None
        for attempt in range(50):
            temp_name = random.choice(REVIEWER_NAMES)
            if temp_name not in used_names:
                author_name = temp_name
                used_names.add(author_name)
                break
        
        # 중복을 피할 수 없으면 그냥 사용
        if author_name is None:
            author_name = random.choice(REVIEWER_NAMES)
        
        # 리뷰 데이터 생성
        review = {
            "product_no": product["product_no"],
            "product_code": "",  # 비워둠
            "option": "",  # 상품 옵션 비워둠
            "date": generate_random_datetime(),
            "author": author_name,
            "rating": 5,  # 항상 5점
            "title": review_title,  # 카테고리별 제목 자동 생성
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
    엑셀 파일 생성 (베이핑존/쥬스온 양식)
    리뷰에이드 업로드 형식: 1행 헤더, 2행 설명, 3행부터 데이터
    열 매핑: A=product_no, D=작성일, E=작성자, F=별점, G=제목, H=내용
    :param reviews: 리뷰 데이터 리스트
    :param output_path: 저장할 파일 경로
    """
    # 새 워크북 생성
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Sheet1"
    
    # 1행: 헤더 작성
    headers = [
        "product_no",      # A열
        "product_code",    # B열
        "상품 옵션",        # C열
        "작성일",           # D열
        "작성자",           # E열
        "별점",             # F열
        "제목",             # G열
        "내용",             # H열
        "이미지 URL 1",     # I열
        "이미지 URL 2",     # J열
        "이미지 URL 3",     # K열
        "이미지 URL 4"      # L열
    ]
    
    for col_idx, header in enumerate(headers, 1):
        ws.cell(row=1, column=col_idx, value=header)
    
    # 2행: 설명 작성 (리뷰에이드 양식 - example.xlsx 정확히 일치)
    descriptions = [
        "상품의 고유번호*\n리뷰에이드 어드민의 상품관리 탭에서 \n상품의 고유번호를 빠르게 확인할 수 있습니다. \n*product_no나 product_code 들 중\n하나만 입력해 주세요.",  # A열
        "상품코드*\n리뷰에이드 어드민의 상품관리 탭에서 \n상품코드를 빠르게 확인할 수 있습니다. \n*product_no나 product_code 들 중\n하나만 입력해 주세요.",  # B열
        "상품 옵션\n미입력시 공란으로 표시됩니다.",  # C열
        "리뷰 작성일*\nYYYY-MM-DD hh:mm:ss\n시간 미 입력 시 00:00:00으로 입력됩니다.",  # D열
        "리뷰 작성자 이름*",  # E열
        "리뷰 별점 \n1~5점의 만족도\n미 입력 시 별점 5점으로 입력됩니다.",  # F열
        "미 입력 시 리뷰 내용이 입력됩니다.\n제목 글자 수는 최대 250자로 제한됩니다. \n초과된 글자는 잘려서 보입니다.",  # G열
        "리뷰 내용*",  # H열
        "",  # I열
        "",  # J열
        "",  # K열
        ""   # L열
    ]
    
    for col_idx, desc in enumerate(descriptions, 1):
        ws.cell(row=2, column=col_idx, value=desc)
    
    # 3행부터: 리뷰 데이터 작성
    for row_idx, review in enumerate(reviews, 3):  # 3행부터 시작
        ws.cell(row=row_idx, column=1, value=review["product_no"])      # A열
        ws.cell(row=row_idx, column=2, value=review["product_code"])    # B열
        ws.cell(row=row_idx, column=3, value=review["option"])          # C열
        ws.cell(row=row_idx, column=4, value=review["date"])            # D열
        ws.cell(row=row_idx, column=5, value=review["author"])          # E열
        ws.cell(row=row_idx, column=6, value=review["rating"])          # F열
        ws.cell(row=row_idx, column=7, value=review["title"])           # G열
        ws.cell(row=row_idx, column=8, value=review["content"])         # H열
        ws.cell(row=row_idx, column=9, value=review["image1"])          # I열
        ws.cell(row=row_idx, column=10, value=review["image2"])         # J열
        ws.cell(row=row_idx, column=11, value=review["image3"])         # K열
        ws.cell(row=row_idx, column=12, value=review["image4"])         # L열
    
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
