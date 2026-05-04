from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
import pandas as pd
import os
from datetime import datetime, timedelta
import random
import io
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill

app = Flask(__name__)
CORS(app)

DATA_DIR = 'data'

# 채널별 엑셀 파일 매핑
CHANNEL_FILES = {
    'vapingzone': '베이핑존.xlsx',
    'juiceon': '쥬스온.xlsx',
    'kukdae': '국대쥬스.xlsx'
}

# 한글 이름 생성용 성씨와 이름
KOREAN_SURNAMES = ['김', '이', '박', '최', '정', '강', '조', '윤', '장', '임', '한', '오', '서', '신', '권', '황', '안', '송', '류', '전']
KOREAN_NAMES = ['민준', '서준', '예준', '도윤', '시우', '주원', '하준', '지호', '준서', '건우',
                '서연', '서윤', '지우', '서현', '민서', '하은', '지민', '수아', '예은', '지유',
                '현우', '민재', '시현', '태양', '승우', '유진', '은서', '채원', '다은', '수빈']

def generate_korean_name():
    """3글자 한글 이름 생성"""
    surname = random.choice(KOREAN_SURNAMES)
    name = random.choice(KOREAN_NAMES)
    return f"{surname}{name}"

def load_products(channel):
    """채널별 상품 데이터 로드"""
    if channel not in CHANNEL_FILES:
        return []
    
    file_path = os.path.join(DATA_DIR, CHANNEL_FILES[channel])
    if not os.path.exists(file_path):
        return []
    
    try:
        df = pd.read_excel(file_path)
        products = []
        for _, row in df.iterrows():
            # 카테고리 필드가 있으면 사용, 없으면 자동 감지
            category = row.get('카테고리', detect_category(str(row['상품명'])))
            products.append({
                'product_no': str(row['상품번호']),
                'product_name': str(row['상품명']),
                'category': category
            })
        return products
    except Exception as e:
        print(f"상품 로드 오류: {e}")
        return []

def save_products(channel, products):
    """채널별 상품 데이터 저장"""
    if channel not in CHANNEL_FILES:
        return False
    
    file_path = os.path.join(DATA_DIR, CHANNEL_FILES[channel])
    
    try:
        df = pd.DataFrame([
            {
                '상품번호': p['product_no'], 
                '상품명': p['product_name'],
                '카테고리': p.get('category', '기타')
            }
            for p in products
        ])
        df.to_excel(file_path, index=False)
        return True
    except Exception as e:
        print(f"상품 저장 오류: {e}")
        return False

@app.route('/')
def index():
    return jsonify({
        'service': '베이핑존 리뷰 자동 생성기 API v2.0',
        'version': '2.0.0',
        'endpoints': [
            'GET /api/products/<channel> - 상품 목록 조회',
            'POST /api/products/<channel> - 상품 추가',
            'PUT /api/products/<channel>/<product_no> - 상품 수정',
            'DELETE /api/products/<channel>/<product_no> - 상품 삭제',
            'GET /api/products/<channel>/download - 상품 엑셀 다운로드',
            'POST /api/generate-reviews - 리뷰 생성',
            'GET /health - 헬스 체크'
        ]
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

# ===== 상품 관리 API =====

@app.route('/api/products/<channel>', methods=['GET'])
def get_products(channel):
    """상품 목록 조회"""
    products = load_products(channel)
    return jsonify(products)

@app.route('/api/products/<channel>', methods=['POST'])
def add_product(channel):
    """상품 추가 (중복 체크)"""
    data = request.get_json()
    product_no = str(data.get('product_no', '')).strip()
    product_name = str(data.get('product_name', '')).strip()
    category = data.get('category', '기타')
    
    if not product_no or not product_name:
        return jsonify({'error': '상품번호와 상품명은 필수입니다'}), 400
    
    products = load_products(channel)
    
    # 중복 체크
    if any(p['product_no'] == product_no for p in products):
        return jsonify({'error': f'상품번호 {product_no}는 이미 존재합니다'}), 409
    
    # 새 상품 추가
    new_product = {
        'product_no': product_no, 
        'product_name': product_name,
        'category': category
    }
    products.append(new_product)
    
    if save_products(channel, products):
        return jsonify({'message': '상품이 추가되었습니다', 'product': new_product}), 201
    else:
        return jsonify({'error': '상품 저장 실패'}), 500

@app.route('/api/products/<channel>/<product_no>', methods=['PUT'])
def update_product(channel, product_no):
    """상품 수정"""
    data = request.get_json()
    new_product_no = str(data.get('product_no', '')).strip()
    new_product_name = str(data.get('product_name', '')).strip()
    new_category = data.get('category', '기타')
    
    if not new_product_no or not new_product_name:
        return jsonify({'error': '상품번호와 상품명은 필수입니다'}), 400
    
    products = load_products(channel)
    
    # 기존 상품 찾기
    product_found = False
    for i, p in enumerate(products):
        if p['product_no'] == product_no:
            # 상품번호를 변경하는 경우 중복 체크
            if new_product_no != product_no:
                if any(p['product_no'] == new_product_no for p in products):
                    return jsonify({'error': f'상품번호 {new_product_no}는 이미 존재합니다'}), 409
            
            # 상품 정보 업데이트
            updated_product = {
                'product_no': new_product_no, 
                'product_name': new_product_name,
                'category': new_category
            }
            products[i] = updated_product
            product_found = True
            break
    
    if not product_found:
        return jsonify({'error': f'상품번호 {product_no}를 찾을 수 없습니다'}), 404
    
    if save_products(channel, products):
        return jsonify({
            'message': '상품이 수정되었습니다',
            'product': updated_product
        }), 200
    else:
        return jsonify({'error': '상품 저장 실패'}), 500

@app.route('/api/products/<channel>/<product_no>', methods=['DELETE'])
def delete_product(channel, product_no):
    """상품 삭제"""
    products = load_products(channel)
    
    # 삭제할 상품 찾기
    original_count = len(products)
    products = [p for p in products if p['product_no'] != product_no]
    
    if len(products) == original_count:
        return jsonify({'error': f'상품번호 {product_no}를 찾을 수 없습니다'}), 404
    
    if save_products(channel, products):
        return jsonify({'message': f'상품번호 {product_no}가 삭제되었습니다'}), 200
    else:
        return jsonify({'error': '상품 삭제 실패'}), 500

@app.route('/api/products/<channel>/download', methods=['GET'])
def download_products(channel):
    """상품 엑셀 다운로드"""
    if channel not in CHANNEL_FILES:
        return jsonify({'error': '잘못된 채널입니다'}), 400
    
    file_path = os.path.join(DATA_DIR, CHANNEL_FILES[channel])
    if not os.path.exists(file_path):
        return jsonify({'error': '파일이 존재하지 않습니다'}), 404
    
    channel_names = {
        'vapingzone': '베이핑존',
        'juiceon': '쥬스온',
        'kukdae': '국대쥬스'
    }
    
    return send_file(
        file_path,
        as_attachment=True,
        download_name=f"{channel_names.get(channel, channel)}_상품목록_{datetime.now().strftime('%Y%m%d')}.xlsx"
    )

# ===== 리뷰 생성 API =====

# 리뷰 템플릿 (40-50자)
REVIEW_TEMPLATES = {
    '액상': [
        "{flavor} 맛이 정말 진하고 좋아요. 목넘김도 부드럽고 만족스러워요.",
        "처음 써보는데 {flavor} 향이 자극적이지 않고 은은해서 좋네요.",
        "{flavor} 특유의 달콤함이 일품이에요. 계속 피게 되는 맛이에요.",
        "생각보다 {flavor} 맛이 진해서 놀랐어요. 재구매 의사 100%입니다.",
        "{flavor} 향이 입안 가득 퍼지는 느낌이 좋아요. 추천합니다!",
    ],
    '기기': [
        "디자인이 깔끔하고 휴대성도 좋아요. 성능도 만족스럽습니다.",
        "배터리 오래가고 연무량도 충분해요. 가성비 최고예요!",
        "처음 전자담배 입문하는데 사용하기 편하고 좋네요.",
        "케이스 질감도 고급스럽고 버튼 조작이 직관적이에요.",
        "생각보다 크기가 작아서 주머니에 쏙 들어가요. 편해요!",
    ],
    '일회용': [
        "일회용치고 연무량 엄청 많아요. 가격 대비 퍼프 수 좋아요.",
        "디자인도 예쁘고 맛도 괜찮아요. 휴대하기 정말 편합니다.",
        "충전 필요 없어서 편하고 {flavor} 맛도 깔끔해요.",
        "처음 써본 일회용인데 생각보다 오래가네요. 만족해요!",
        "가격 저렴한데 퍼프 수도 많고 연무도 부드러워요. 굿!",
    ]
}

def detect_category(product_name):
    """상품명으로 카테고리 자동 감지"""
    if any(keyword in product_name for keyword in ['액상', '니코틴', 'ml', 'ML']):
        return '액상'
    elif any(keyword in product_name for keyword in ['일회용', 'PUFF', 'puff', '퍼프']):
        return '일회용'
    else:
        return '기기'

def extract_flavor(product_name):
    """상품명에서 맛/향 추출"""
    flavors = ['딸기', '수박', '청포도', '복숭아', '민트', '망고', '블루베리', '자몽', 
               '레몬', '체리', '사과', '포도', '바닐라', '커피', '코코넛']
    for flavor in flavors:
        if flavor in product_name:
            return flavor
    return '이'

@app.route('/api/generate-reviews', methods=['POST'])
def generate_reviews():
    """리뷰 생성"""
    data = request.get_json()
    channel = data.get('channel', 'vapingzone')
    count = min(int(data.get('count', 10)), 100)
    
    products = load_products(channel)
    if not products:
        return jsonify({'error': '상품 데이터가 없습니다'}), 400
    
    reviews = []
    now = datetime.now()
    
    for i in range(count):
        product = random.choice(products)
        category = detect_category(product['product_name'])
        flavor = extract_flavor(product['product_name'])
        
        # 템플릿 선택 및 치환
        template = random.choice(REVIEW_TEMPLATES[category])
        review_text = template.format(flavor=flavor)
        
        # 제목은 리뷰 내용 30자 요약
        title = review_text[:30] + ('...' if len(review_text) > 30 else '')
        
        # 날짜: 어제~3일 전
        days_ago = random.randint(1, 3)
        review_date = now - timedelta(days=days_ago)
        
        reviews.append({
            '작성자': generate_korean_name(),
            '제목': title,
            '내용': review_text,
            '평점': random.choice([4, 5]),
            '작성일': review_date.strftime('%Y-%m-%d %H:%M:%S'),
            '상품번호': product['product_no'],
            '상품명': product['product_name']
        })
    
    # 엑셀 생성
    df = pd.DataFrame(reviews)
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='리뷰')
        worksheet = writer.sheets['리뷰']
        
        # 스타일 적용
        for cell in worksheet[1]:
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color='CCE5FF', end_color='CCE5FF', fill_type='solid')
            cell.alignment = Alignment(horizontal='center')
        
        # 열 너비 조정
        worksheet.column_dimensions['A'].width = 12
        worksheet.column_dimensions['B'].width = 35
        worksheet.column_dimensions['C'].width = 50
        worksheet.column_dimensions['D'].width = 8
        worksheet.column_dimensions['E'].width = 20
        worksheet.column_dimensions['F'].width = 12
        worksheet.column_dimensions['G'].width = 40
    
    output.seek(0)
    
    channel_names = {
        'vapingzone': '베이핑존',
        'juiceon': '쥬스온',
        'kukdae': '국대쥬스'
    }
    
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f"{channel_names.get(channel, channel)}_리뷰_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
