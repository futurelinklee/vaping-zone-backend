#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask 백엔드 API 서버
Flutter Web에서 호출할 수 있는 REST API 제공
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import subprocess
import json
import os

app = Flask(__name__)
CORS(app)  # CORS 허용

@app.route('/api/load-products', methods=['GET'])
def load_products():
    """상품 리스트 로드"""
    try:
        channel = request.args.get('channel', 'cafe24')  # 기본값은 cafe24
        
        # 채널별 파일 경로
        file_map = {
            'cafe24': '/home/user/cafe24_review_generator/data/products.xlsx',
            'juiceon': '/home/user/cafe24_review_generator/data/juiceon_products.json',
            'kukdae': '/home/user/cafe24_review_generator/data/kukdae_products.json'
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
        
        # Excel 파일인 경우 기존 스크립트 실행
        result = subprocess.run(
            ['python3', '/home/user/cafe24_review_generator/scripts/load_products.py', file_path],
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
            'cafe24': '/home/user/cafe24_review_generator/data/upload_template.xlsx',
            'juiceon': '/home/user/cafe24_review_generator/data/juiceon_template.xlsx',
            'kukdae': '/home/user/cafe24_review_generator/data/kukdae_template.xlsx'
        }
        
        # 채널별 스크립트 선택 (국대쥬스는 전용 스크립트 사용)
        script_map = {
            'cafe24': '/home/user/cafe24_review_generator/scripts/generate_reviews_with_gpt.py',
            'juiceon': '/home/user/cafe24_review_generator/scripts/generate_reviews_with_gpt.py',
            'kukdae': '/home/user/cafe24_review_generator/scripts/generate_reviews_kukdae.py'
        }
        
        template_path = template_map.get(channel, template_map['cafe24'])
        script_path = script_map.get(channel, script_map['cafe24'])
        output_filename = f'{channel}_reviews.xlsx'
        output_path = f'/home/user/{output_filename}'
        
        # JSON 데이터 준비
        json_data = json.dumps({
            'products': data.get('products', []),
            'count': data.get('count', 10),
            'template': template_path,
            'output': output_path,
        })
        
        result = subprocess.run(
            ['python3', script_path, json_data],
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

@app.route('/api/auto-upload', methods=['POST'])
def auto_upload():
    """ReviewAid 자동 업로드"""
    try:
        data = request.get_json()
        excel_path = data.get('file_path', '/home/user/cafe24_reviews.xlsx')
        
        result = subprocess.run(
            ['python3', '/home/user/cafe24_review_generator/scripts/auto_upload_reviewaid_final.py', excel_path],
            capture_output=True,
            text=True,
            timeout=180
        )
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            return jsonify(response)
        else:
            return jsonify({
                'success': False,
                'error': f'업로드 실패: {result.stderr}'
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
        excel_path = f'/home/user/{channel}_reviews.xlsx'
        
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
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    print("🚀 카페24 리뷰 생성기 백엔드 API 서버 시작")
    print("📍 포트: 5000")
    print("📍 상품 로드: GET /api/load-products")
    print("📍 리뷰 생성: POST /api/generate-reviews")
    print("📍 자동 업로드: POST /api/auto-upload")
    app.run(host='0.0.0.0', port=5000, debug=False)
