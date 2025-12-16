#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ReviewAid 사이트 자동 업로드
https://www.reviewaid.ai/review-upload
"""

import sys
import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

REVIEWAID_UPLOAD_URL = "https://www.reviewaid.ai/review-upload"

def upload_to_reviewaid(excel_path):
    """
    ReviewAid 사이트에 엑셀 파일 업로드
    
    :param excel_path: 업로드할 엑셀 파일 경로
    :return: 성공 여부 딕셔너리
    """
    
    # Chrome 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    # 파일 다운로드 방지
    chrome_options.add_experimental_option('prefs', {
        'download.prompt_for_download': False,
        'download.directory_upgrade': True,
        'safebrowsing.enabled': True
    })
    
    driver = None
    screenshots = {}
    
    try:
        print("=" * 70)
        print("🤖 ReviewAid 자동 업로드 시작")
        print("=" * 70)
        
        # ChromeDriver 실행
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(30)
        wait = WebDriverWait(driver, 15)
        
        # Step 1: 페이지 접속
        print(f"\n[Step 1] 📂 ReviewAid 업로드 페이지 접속 중...")
        print(f"URL: {REVIEWAID_UPLOAD_URL}")
        driver.get(REVIEWAID_UPLOAD_URL)
        time.sleep(3)
        
        # 초기 스크린샷
        screenshot_path = "/home/user/reviewaid_step1_initial.png"
        driver.save_screenshot(screenshot_path)
        screenshots['step1_initial'] = screenshot_path
        print(f"✅ 페이지 로드 완료")
        print(f"📸 스크린샷: {screenshot_path}")
        
        # Step 2: "대량 업로드" 버튼 찾기
        print(f"\n[Step 2] 🔍 '대량 업로드' 버튼 찾는 중...")
        
        bulk_upload_button = None
        
        # 방법 1: 클래스명으로 찾기
        try:
            buttons = driver.find_elements(By.CSS_SELECTOR, "button.AdminButton_AdminButton__gjQ9r.AdminButton_size-40__3Tovi")
            for btn in buttons:
                if "대량 업로드" in btn.text or "bulk" in btn.text.lower():
                    bulk_upload_button = btn
                    print(f"✅ 버튼 발견 (CSS Selector): {btn.text}")
                    break
        except Exception as e:
            print(f"⚠️ CSS Selector 실패: {e}")
        
        # 방법 2: XPath로 텍스트 검색
        if not bulk_upload_button:
            try:
                bulk_upload_button = driver.find_element(By.XPATH, "//button[contains(text(), '대량 업로드')]")
                print(f"✅ 버튼 발견 (XPath): {bulk_upload_button.text}")
            except Exception as e:
                print(f"⚠️ XPath 실패: {e}")
        
        # 방법 3: 모든 버튼 검색
        if not bulk_upload_button:
            try:
                all_buttons = driver.find_elements(By.TAG_NAME, "button")
                print(f"🔍 전체 버튼 수: {len(all_buttons)}")
                for idx, btn in enumerate(all_buttons):
                    btn_text = btn.text.strip()
                    if btn_text:
                        print(f"   버튼 {idx+1}: '{btn_text}'")
                    if "대량" in btn_text or "업로드" in btn_text or "bulk" in btn_text.lower():
                        bulk_upload_button = btn
                        print(f"✅ 버튼 발견 (전체 검색): {btn_text}")
                        break
            except Exception as e:
                print(f"⚠️ 전체 검색 실패: {e}")
        
        if not bulk_upload_button:
            raise Exception("'대량 업로드' 버튼을 찾을 수 없습니다")
        
        # Step 3: 버튼 클릭 전 스크린샷
        screenshot_path = "/home/user/reviewaid_step2_before_click.png"
        driver.save_screenshot(screenshot_path)
        screenshots['step2_before_click'] = screenshot_path
        print(f"📸 클릭 전 스크린샷: {screenshot_path}")
        
        # Step 4: "대량 업로드" 버튼 클릭
        print(f"\n[Step 3] 🖱️ '대량 업로드' 버튼 클릭 중...")
        
        # 버튼이 보이고 클릭 가능할 때까지 대기
        wait.until(EC.element_to_be_clickable(bulk_upload_button))
        
        # JavaScript로 스크롤하여 버튼이 보이도록
        driver.execute_script("arguments[0].scrollIntoView(true);", bulk_upload_button)
        time.sleep(1)
        
        # 클릭 시도
        try:
            bulk_upload_button.click()
            print("✅ 버튼 클릭 성공 (일반 클릭)")
        except Exception as e:
            print(f"⚠️ 일반 클릭 실패, JavaScript 클릭 시도: {e}")
            driver.execute_script("arguments[0].click();", bulk_upload_button)
            print("✅ 버튼 클릭 성공 (JavaScript 클릭)")
        
        time.sleep(2)
        
        # Step 5: 파일 업로드 input 찾기
        print(f"\n[Step 4] 🔍 파일 업로드 input 찾는 중...")
        
        # 클릭 후 스크린샷
        screenshot_path = "/home/user/reviewaid_step3_after_click.png"
        driver.save_screenshot(screenshot_path)
        screenshots['step3_after_click'] = screenshot_path
        print(f"📸 클릭 후 스크린샷: {screenshot_path}")
        
        # 파일 input 찾기
        file_input = None
        
        # 방법 1: type='file' 찾기
        try:
            file_inputs = driver.find_elements(By.CSS_SELECTOR, "input[type='file']")
            print(f"🔍 발견된 파일 input 수: {len(file_inputs)}")
            
            # 보이는 것 또는 숨겨진 것 모두 시도
            for idx, inp in enumerate(file_inputs):
                try:
                    # display 속성 확인
                    is_displayed = inp.is_displayed()
                    print(f"   Input {idx+1}: displayed={is_displayed}")
                    
                    # 숨겨진 input도 사용 가능
                    file_input = inp
                    print(f"✅ 파일 input 발견 (input {idx+1})")
                    break
                except:
                    continue
        except Exception as e:
            print(f"⚠️ 파일 input 검색 실패: {e}")
        
        if not file_input:
            # 페이지 소스 저장
            with open('/home/user/reviewaid_page_source.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print(f"📄 페이지 소스 저장: /home/user/reviewaid_page_source.html")
            
            raise Exception("파일 업로드 input을 찾을 수 없습니다")
        
        # Step 6: 파일 업로드
        print(f"\n[Step 5] 📤 파일 업로드 중...")
        print(f"파일 경로: {excel_path}")
        
        file_input.send_keys(excel_path)
        print(f"✅ 파일 선택 완료")
        
        time.sleep(3)
        
        # Step 7: 업로드 완료 확인
        screenshot_path = "/home/user/reviewaid_step4_file_selected.png"
        driver.save_screenshot(screenshot_path)
        screenshots['step4_file_selected'] = screenshot_path
        print(f"📸 파일 선택 후 스크린샷: {screenshot_path}")
        
        # 확인/등록 버튼 찾기
        print(f"\n[Step 6] 🔍 확인/등록 버튼 찾는 중...")
        
        submit_button = None
        submit_selectors = [
            "//button[contains(text(), '확인')]",
            "//button[contains(text(), '등록')]",
            "//button[contains(text(), '업로드')]",
            "//button[contains(text(), '저장')]",
            "//button[@type='submit']",
            "button[type='submit']",
        ]
        
        for selector in submit_selectors:
            try:
                if selector.startswith('//'):
                    buttons = driver.find_elements(By.XPATH, selector)
                else:
                    buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                
                for btn in buttons:
                    if btn.is_displayed() and btn.is_enabled():
                        submit_button = btn
                        print(f"✅ 확인 버튼 발견: {btn.text}")
                        break
                
                if submit_button:
                    break
            except:
                continue
        
        if submit_button:
            print(f"\n[Step 7] 🖱️ 확인 버튼 클릭 중...")
            
            try:
                submit_button.click()
                print("✅ 확인 버튼 클릭 성공")
            except:
                driver.execute_script("arguments[0].click();", submit_button)
                print("✅ 확인 버튼 클릭 성공 (JavaScript)")
            
            time.sleep(5)
        else:
            print("⚠️ 확인 버튼을 찾지 못했습니다. 파일 선택만 완료되었습니다.")
        
        # 최종 스크린샷
        screenshot_path = "/home/user/reviewaid_step5_final.png"
        driver.save_screenshot(screenshot_path)
        screenshots['step5_final'] = screenshot_path
        print(f"📸 최종 스크린샷: {screenshot_path}")
        
        # 성공 메시지 확인
        print(f"\n[Step 8] ✅ 업로드 결과 확인 중...")
        
        try:
            page_text = driver.page_source.lower()
            success_keywords = ['성공', '완료', '등록되었습니다', 'success', 'complete']
            
            for keyword in success_keywords:
                if keyword in page_text:
                    print(f"✅ 성공 키워드 발견: '{keyword}'")
                    break
        except:
            pass
        
        print("\n" + "=" * 70)
        print("✅ 자동 업로드 프로세스 완료!")
        print("=" * 70)
        print("\n📸 생성된 스크린샷:")
        for name, path in screenshots.items():
            print(f"   - {name}: {path}")
        print("\n💡 스크린샷을 확인하여 업로드 결과를 검증하세요.")
        print("=" * 70)
        
        return {
            'success': True,
            'message': '업로드 프로세스 완료',
            'screenshots': screenshots
        }
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        
        # 에러 스크린샷
        if driver:
            try:
                error_screenshot = "/home/user/reviewaid_error.png"
                driver.save_screenshot(error_screenshot)
                screenshots['error'] = error_screenshot
                print(f"📸 에러 스크린샷: {error_screenshot}")
                
                # 에러 페이지 소스
                with open('/home/user/reviewaid_error.html', 'w', encoding='utf-8') as f:
                    f.write(driver.page_source)
                print(f"📄 에러 페이지 소스: /home/user/reviewaid_error.html")
            except:
                pass
        
        return {
            'success': False,
            'error': str(e),
            'screenshots': screenshots
        }
        
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
        
        # 절대 경로로 변환
        excel_path = os.path.abspath(excel_path)
        
        if not os.path.exists(excel_path):
            raise Exception(f"파일이 존재하지 않습니다: {excel_path}")
        
        result = upload_to_reviewaid(excel_path)
        
        print(json.dumps(result, ensure_ascii=False))
        
        if not result['success']:
            sys.exit(1)
        
    except Exception as e:
        result = {
            "success": False,
            "error": str(e)
        }
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(1)

if __name__ == "__main__":
    import os
    main()
