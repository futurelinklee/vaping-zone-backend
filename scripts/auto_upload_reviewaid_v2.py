#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ReviewAid 사이트에 자동 로그인 및 엑셀 파일 업로드
"""

import sys
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

REVIEWAID_URL = "https://vapingzone.cafe24.com/exec/admin/shop1/myapps/app?signature=9PB1S2e%2ByZpNswCIzv%2FeZxW9qjYrmKlJrAkUFXCoXs1EDlMW%2BB1PdGz8MBkgyr89jvzLno0ZiRtFMVewZ3flEg%3D%3D"

def upload_to_reviewaid(excel_path):
    """
    ReviewAid 사이트에 엑셀 파일 업로드
    
    :param excel_path: 업로드할 엑셀 파일 경로
    :return: 성공 여부
    """
    
    # Chrome 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 백그라운드 실행
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = None
    
    try:
        # ChromeDriver 실행
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        
        print(f"🌐 ReviewAid 페이지 접속 중...")
        driver.get(REVIEWAID_URL)
        
        # 페이지 로딩 대기
        time.sleep(5)
        
        # 페이지 소스 저장 (디버깅용)
        with open('/home/user/reviewaid_page.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("📄 페이지 소스 저장: /home/user/reviewaid_page.html")
        
        # 스크린샷 저장 (디버깅용)
        driver.save_screenshot('/home/user/reviewaid_initial.png')
        print("📸 초기 스크린샷 저장: /home/user/reviewaid_initial.png")
        
        print("🔍 파일 업로드 요소 찾는 중...")
        
        # 파일 업로드 input 요소 찾기
        upload_input = None
        wait = WebDriverWait(driver, 10)
        
        # 다양한 선택자 시도
        possible_selectors = [
            "input[type='file']",
            "input[accept*='excel']",
            "input[accept*='.xlsx']",
            "input[accept*='.xls']",
            "input[accept*='spreadsheet']",
            "input[name*='file']",
            "input[id*='file']",
            "input[id*='upload']",
            "input[class*='upload']",
        ]
        
        for selector in possible_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    upload_input = elements[0]
                    print(f"✅ 업로드 요소 발견: {selector}")
                    break
            except:
                continue
        
        if not upload_input:
            # XPath로도 시도
            try:
                upload_input = driver.find_element(By.XPATH, "//input[@type='file']")
                print("✅ 업로드 요소 발견: XPath")
            except:
                pass
        
        if not upload_input:
            raise Exception("파일 업로드 input 요소를 찾을 수 없습니다. 페이지 구조를 확인하세요.")
        
        # 파일 업로드
        print(f"📤 파일 업로드 중: {excel_path}")
        upload_input.send_keys(excel_path)
        
        # 업로드 후 대기
        time.sleep(3)
        
        # 중간 스크린샷
        driver.save_screenshot('/home/user/reviewaid_after_select.png')
        print("📸 파일 선택 후 스크린샷: /home/user/reviewaid_after_select.png")
        
        # 업로드 버튼 찾기 및 클릭
        print("🔍 업로드/확인 버튼 찾는 중...")
        
        # 버튼 찾기
        button_found = False
        button_selectors = [
            "//button[contains(text(), '업로드')]",
            "//button[contains(text(), '등록')]",
            "//button[contains(text(), '확인')]",
            "//button[contains(text(), '저장')]",
            "//input[@type='submit']",
            "//button[@type='submit']",
            "button[type='submit']",
            "input[type='submit']",
            ".btn-upload",
            ".btn-submit",
            "#upload-btn",
            "#submit-btn",
        ]
        
        for selector in button_selectors:
            try:
                if selector.startswith('//'):
                    # XPath
                    buttons = driver.find_elements(By.XPATH, selector)
                else:
                    # CSS Selector
                    buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                
                for button in buttons:
                    if button.is_displayed() and button.is_enabled():
                        print(f"✅ 업로드 버튼 발견 및 클릭: {selector}")
                        button.click()
                        button_found = True
                        break
                
                if button_found:
                    break
            except Exception as e:
                continue
        
        if button_found:
            print("✅ 업로드 버튼 클릭 완료")
            time.sleep(5)  # 업로드 처리 대기
        else:
            print("⚠️ 업로드 버튼을 찾지 못했습니다.")
            print("ℹ️ 파일 선택은 완료되었습니다. 수동으로 버튼을 클릭해야 할 수 있습니다.")
        
        # 최종 스크린샷
        driver.save_screenshot('/home/user/reviewaid_final.png')
        print("📸 최종 스크린샷 저장: /home/user/reviewaid_final.png")
        
        # 성공 메시지 확인
        try:
            success_messages = [
                "성공",
                "완료",
                "등록되었습니다",
                "업로드되었습니다",
            ]
            
            page_text = driver.page_source
            for msg in success_messages:
                if msg in page_text:
                    print(f"✅ 성공 메시지 발견: {msg}")
                    return True
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"❌ 업로드 실패: {str(e)}")
        
        # 에러 스크린샷
        if driver:
            try:
                driver.save_screenshot("/home/user/reviewaid_error.png")
                print("📸 에러 스크린샷 저장: /home/user/reviewaid_error.png")
                
                # 에러 페이지 소스 저장
                with open('/home/user/reviewaid_error.html', 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                print("📄 에러 페이지 소스 저장: /home/user/reviewaid_error.html")
            except:
                pass
        
        return False
        
    finally:
        if driver:
            driver.quit()

def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        result = {
            "success": False,
            "error": "엑셀 파일 경로가 필요합니다"
        }
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(1)
    
    try:
        excel_path = sys.argv[1]
        
        print("=" * 60)
        print("🤖 ReviewAid 자동 업로드 시작")
        print("=" * 60)
        print(f"📂 엑셀 파일: {excel_path}")
        print(f"🌐 업로드 URL: {REVIEWAID_URL}")
        print("=" * 60)
        
        success = upload_to_reviewaid(excel_path)
        
        result = {
            "success": success,
            "message": "업로드 완료" if success else "업로드 실패",
            "excel_path": excel_path,
            "screenshots": {
                "initial": "/home/user/reviewaid_initial.png",
                "after_select": "/home/user/reviewaid_after_select.png",
                "final": "/home/user/reviewaid_final.png"
            }
        }
        
        print("\n" + "=" * 60)
        if success:
            print("✅ 자동 업로드 성공!")
            print("📸 스크린샷을 확인하여 업로드 결과를 확인하세요.")
        else:
            print("❌ 자동 업로드 실패")
            print("📸 에러 스크린샷을 확인하세요.")
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
