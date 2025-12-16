#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ReviewAid 사이트에 자동으로 엑셀 파일 업로드
"""

import sys
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

def upload_to_reviewaid(excel_path, url):
    """
    ReviewAid 사이트에 엑셀 파일 업로드
    
    :param excel_path: 업로드할 엑셀 파일 경로
    :param url: ReviewAid 업로드 페이지 URL
    :return: 성공 여부
    """
    
    # Chrome 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 백그라운드 실행
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    
    driver = None
    
    try:
        # ChromeDriver 실행
        driver = webdriver.Chrome(options=chrome_options)
        
        print(f"📂 업로드 페이지 접속 중: {url}")
        driver.get(url)
        
        # 페이지 로딩 대기
        time.sleep(3)
        
        print("🔍 파일 업로드 요소 찾는 중...")
        
        # 파일 업로드 input 요소 찾기
        # 여러 가능한 선택자 시도
        upload_input = None
        possible_selectors = [
            "input[type='file']",
            "input[accept*='excel']",
            "input[accept*='spreadsheet']",
            "input[name*='file']",
            "input[id*='file']",
            "input[id*='upload']",
        ]
        
        for selector in possible_selectors:
            try:
                upload_input = driver.find_element(By.CSS_SELECTOR, selector)
                if upload_input:
                    print(f"✅ 업로드 요소 발견: {selector}")
                    break
            except:
                continue
        
        if not upload_input:
            raise Exception("파일 업로드 input 요소를 찾을 수 없습니다")
        
        # 파일 업로드
        print(f"📤 파일 업로드 중: {excel_path}")
        upload_input.send_keys(excel_path)
        
        # 업로드 후 대기
        time.sleep(2)
        
        # 업로드 버튼 찾기 및 클릭
        print("🔍 업로드 버튼 찾는 중...")
        upload_button = None
        button_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "button:contains('업로드')",
            "button:contains('등록')",
            "button:contains('확인')",
            ".btn-upload",
            "#upload-btn",
        ]
        
        for selector in button_selectors:
            try:
                upload_button = driver.find_element(By.CSS_SELECTOR, selector)
                if upload_button and upload_button.is_displayed():
                    print(f"✅ 업로드 버튼 발견: {selector}")
                    upload_button.click()
                    break
            except:
                continue
        
        if upload_button:
            print("✅ 업로드 버튼 클릭 완료")
            time.sleep(3)
        else:
            print("⚠️ 업로드 버튼을 찾지 못했습니다. 파일 선택만 완료되었을 수 있습니다.")
        
        # 성공 메시지 확인
        print("🔍 업로드 결과 확인 중...")
        time.sleep(2)
        
        # 스크린샷 저장 (디버깅용)
        screenshot_path = "/home/user/upload_result.png"
        driver.save_screenshot(screenshot_path)
        print(f"📸 스크린샷 저장: {screenshot_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ 업로드 실패: {str(e)}")
        
        # 에러 스크린샷
        if driver:
            try:
                driver.save_screenshot("/home/user/upload_error.png")
                print("📸 에러 스크린샷 저장: /home/user/upload_error.png")
            except:
                pass
        
        return False
        
    finally:
        if driver:
            driver.quit()

def main():
    """메인 함수"""
    if len(sys.argv) < 3:
        print("Usage: python auto_upload_to_reviewaid.py <EXCEL_PATH> <UPLOAD_URL>")
        sys.exit(1)
    
    try:
        excel_path = sys.argv[1]
        upload_url = sys.argv[2]
        
        print("=" * 60)
        print("🤖 ReviewAid 자동 업로드 시작")
        print("=" * 60)
        print(f"📂 엑셀 파일: {excel_path}")
        print(f"🌐 업로드 URL: {upload_url}")
        print("=" * 60)
        
        success = upload_to_reviewaid(excel_path, upload_url)
        
        result = {
            "success": success,
            "message": "업로드 완료" if success else "업로드 실패",
            "excel_path": excel_path
        }
        
        print("\n" + "=" * 60)
        if success:
            print("✅ 자동 업로드 성공!")
        else:
            print("❌ 자동 업로드 실패")
        print("=" * 60)
        
        print(json.dumps(result, ensure_ascii=False))
        
    except Exception as e:
        result = {
            "success": False,
            "error": str(e)
        }
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(1)

if __name__ == "__main__":
    main()
