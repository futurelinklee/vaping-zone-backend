from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
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
    """3글자 한글 이름 생성"""  # ← 이 줄 확인
    surname = random.choice(KOREAN_SURNAMES)
    name = random.choice(KOREAN_NAMES)
    return f"{surname}{name}"

def load_products(channel):
    """채널별 상품
... (output truncated, click Expand to see full output)
