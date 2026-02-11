#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
베이핑존 리뷰 자동 생성기 - Flask 백엔드 API 서버
Railway/Render 배포용
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import subprocess
import json
import os
import sys

app = Flask(__name__)
CORS(app)  # CORS 허용

# 배포 환경에서 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/api/load-products', methods=['GET'])
def load_products():
    """상품 리스트 로드"""
    try:
        channel = request.args.get('channel', 'cafe24')
        
        # 채널별 파일 경로
        file_map = {
            'cafe24': os.path.join(BASE_DIR, 'data/products.xlsx'),
            'juiceon': os.path.join(BASE_DIR, 'data/juiceon_products.json'),
            'kukdae': os.path.join(BASE_DIR, 'data/kukdae_products.json')
        }
        
        file_path = file_map.get(channel)
        
        if not file_path:
            return jsonify({
                'success': False,
                'error': f'알 수 없는 채널: {channel}'
            }), 400
        
        # JSON 파일인 경우 직접 읽기
        if file_path.endswith('.json'):
            if not os.path.exists(file_path):
                return jsonify({
                    'success': False,
                    'error': f'파일을 찾을 수 없습니다: {file_path}'
                }), 404
            
            with open(file_path, 'r', encoding='utf-8') as f:
                products = json.load(f)
            
            return jsonify({
                'success': True,
                'products': products,
                'count': len(products)
            })
        
        # Excel 파일인 경우 스크립트 실행
        script_path = os.path.join(BASE_DIR, 'scripts/load_products.py')
        result = subprocess.run(
            [sys.executable, script_path, file_path],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            return jsonify(response)
        else:
            return jsonify({
                'success': False,
                'error': f'스크립트 실행 실패: {result.stderr}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/generate-reviews', methods=['POST'])
def generate_reviews():
    """리뷰 생성"""
    try:
        data = request.get_json()
        
        # 환경변수 설정
        env = os.environ.copy()
        if 'api_key' in data:
            env['OPENAI_API_KEY'] = data['api_key']
        
        # 채널별 템플릿 선택
        channel = data.get('channel', 'cafe24')
        template_map = {
            'cafe24': os.path.join(BASE_DIR, 'data/upload_template.xlsx'),
            'juiceon': os.path.join(BASE_DIR, 'data/juiceon_template.xlsx'),
            'kukdae': os.path.join(BASE_DIR, 'data/kukdae_template.xlsx')
        }
        
        # 채널별 스크립트 선택
        script_map = {
            'cafe24': os.path.join(BASE_DIR, 'scripts/generate_reviews_v2.py'),
            'juiceon': os.path.join(BASE_DIR, 'scripts/generate_reviews_v2.py'),
            'kukdae': os.path.join(BASE_DIR, 'scripts/generate_reviews_kukdae.py')
        }
        
        template_path = template_map.get(channel, template_map['cafe24'])
        script_path = script_map.get(channel, script_map['cafe24'])
        output_filename = f'{channel}_reviews.xlsx'
        output_path = os.path.join(BASE_DIR, output_filename)
        
        # JSON 데이터 준비
        json_data = json.dumps({
            'products': data.get('products', []),
            'count': data.get('count', 10),
            'template': template_path,
            'output': output_path,
        })
        
        result = subprocess.run(
            [sys.executable, script_path, json_data],
            capture_output=True,
            text=True,
            env=env,
            timeout=120
        )
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            return jsonify(response)
        else:
            return jsonify({
                'success': False,
                'error': f'리뷰 생성 실패: {result.stderr}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/download-excel', methods=['GET'])
def download_excel():
    """생성된 엑셀 파일 다운로드"""
    try:
        channel = request.args.get('channel', 'cafe24')
        excel_path = os.path.join(BASE_DIR, f'{channel}_reviews.xlsx')
        
        if not os.path.exists(excel_path):
            return jsonify({
                'success': False,
                'error': '엑셀 파일이 없습니다. 먼저 리뷰를 생성해주세요.'
            }), 404
        
        return send_file(
            excel_path,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f'{channel}_reviews.xlsx'
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """헬스체크"""
    return jsonify({'status': 'ok', 'service': 'vaping-zone-review-api'})

@app.route('/', methods=['GET'])
def index():
    """루트 경로"""
    return jsonify({
        'service': '베이핑존 리뷰 자동 생성기 API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'load_products': '/api/load-products?channel=cafe24|juiceon|kukdae',
            'generate_reviews': '/api/generate-reviews (POST)',
            'download_excel': '/api/download-excel?channel=cafe24|juiceon|kukdae'
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 베이핑존 리뷰 생성기 백엔드 API 서버 시작")
    print(f"📍 포트: {port}")
    print(f"📍 상품 로드: GET /api/load-products")
    print(f"📍 리뷰 생성: POST /api/generate-reviews")
    app.run(host='0.0.0.0', port=port, debug=False)

# ============================================
# 상품 관리 API 엔드포인트
# ============================================

@app.route('/api/products/<channel>', methods=['GET'])
def get_products(channel):
    """채널별 상품 목록 조회"""
    try:
        import openpyxl
        
        # 채널별 파일 매핑
        file_map = {
            'vapingzone': 'data/upload_template.xlsx',
            'juiceon': 'data/juiceon_template.xlsx',
            'kukdae': 'data/kukdae_template.xlsx'
        }
        
        if channel not in file_map:
            return jsonify({'error': '유효하지 않은 채널입니다.'}), 400
        
        file_path = os.path.join(BASE_DIR, file_map[channel])
        
        if not os.path.exists(file_path):
            return jsonify({'error': '상품 파일을 찾을 수 없습니다.'}), 404
        
        wb = openpyxl.load_workbook(file_path)
        sheet = wb.active
        
        products = []
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if row[0]:  # product_no가 있으면
                products.append({
                    'product_no': row[0],
                    'category': row[1] if len(row) > 1 else '',
                    'name': row[2] if len(row) > 2 else ''
                })
        
        return jsonify({'products': products, 'count': len(products)})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<channel>', methods=['POST'])
def add_product(channel):
    """상품 추가"""
    try:
        import openpyxl
        
        file_map = {
            'vapingzone': 'data/upload_template.xlsx',
            'juiceon': 'data/juiceon_template.xlsx',
            'kukdae': 'data/kukdae_template.xlsx'
        }
        
        if channel not in file_map:
            return jsonify({'error': '유효하지 않은 채널입니다.'}), 400
        
        data = request.json
        product_no = data.get('product_no')
        category = data.get('category')
        name = data.get('name')
        
        if not all([product_no, category, name]):
            return jsonify({'error': '모든 필드를 입력해주세요.'}), 400
        
        file_path = os.path.join(BASE_DIR, file_map[channel])
        wb = openpyxl.load_workbook(file_path)
        sheet = wb.active
        
        # 중복 체크
        for row in sheet.iter_rows(min_row=2, values_only=True):
            if row[0] == product_no:
                return jsonify({'error': '이미 존재하는 상품번호입니다.'}), 400
        
        # 새 행 추가
        sheet.append([product_no, category, name])
        wb.save(file_path)
        
        return jsonify({'message': '상품이 추가되었습니다.', 'product': data}), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<channel>/<int:product_no>', methods=['DELETE'])
def delete_product(channel, product_no):
    """상품 삭제"""
    try:
        import openpyxl
        
        file_map = {
            'vapingzone': 'data/upload_template.xlsx',
            'juiceon': 'data/juiceon_template.xlsx',
            'kukdae': 'data/kukdae_template.xlsx'
        }
        
        if channel not in file_map:
            return jsonify({'error': '유효하지 않은 채널입니다.'}), 400
        
        file_path = os.path.join(BASE_DIR, file_map[channel])
        wb = openpyxl.load_workbook(file_path)
        sheet = wb.active
        
        # 삭제할 행 찾기
        row_to_delete = None
        for idx, row in enumerate(sheet.iter_rows(min_row=2), start=2):
            if row[0].value == product_no:
                row_to_delete = idx
                break
        
        if row_to_delete is None:
            return jsonify({'error': '상품을 찾을 수 없습니다.'}), 404
        
        sheet.delete_rows(row_to_delete)
        wb.save(file_path)
        
        return jsonify({'message': '상품이 삭제되었습니다.'}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/products/<channel>/download', methods=['GET'])
def download_products(channel):
    """상품 목록 엑셀 다운로드"""
    try:
        file_map = {
            'vapingzone': 'data/upload_template.xlsx',
            'juiceon': 'data/juiceon_template.xlsx',
            'kukdae': 'data/kukdae_template.xlsx'
        }
        
        if channel not in file_map:
            return jsonify({'error': '유효하지 않은 채널입니다.'}), 400
        
        file_path = os.path.join(BASE_DIR, file_map[channel])
        
        if not os.path.exists(file_path):
            return jsonify({'error': '파일을 찾을 수 없습니다.'}), 404
        
        filename = f'{channel}_products.xlsx'
        return send_file(file_path, as_attachment=True, download_name=filename)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

