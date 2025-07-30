#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Selenium을 이용한 티스토리 자동 포스팅
API 없이 웹 브라우저 자동화로 티스토리에 임시발행
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
import time
import random
import os

# webdriver-manager import
try:
    from webdriver_manager.chrome import ChromeDriverManager
    HAS_WEBDRIVER_MANAGER = True
except ImportError:
    HAS_WEBDRIVER_MANAGER = False

class TistorySeleniumPoster:
    def __init__(self):
        self.email = "nigsffetexpress123@gmail.com"
        self.password = "!Redsea1982"
        self.blog_url = "https://talk45667.tistory.com"
        self.driver = None
        
    def setup_driver(self, headless=False):
        """Chrome 드라이버 설정"""
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument("--headless=new")  # 최신 headless 모드
            print("🔧 Headless 모드로 설정")
        
        # GitHub Actions 환경을 위한 옵션들
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-features=TranslateUI")
        chrome_options.add_argument("--disable-ipc-flooding-protection")
        
        # 안정성을 위한 옵션들
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        
        # 자동화 감지 방지
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # User-Agent 설정 (최신)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
        
        # Chrome 바이너리 경로 설정 (GitHub Actions)
        chrome_bin = os.environ.get('CHROME_BIN')
        if chrome_bin:
            chrome_options.binary_location = chrome_bin
            print(f"🔧 Chrome 바이너리 경로: {chrome_bin}")
        
        # 로깅 레벨 설정
        chrome_options.add_argument("--log-level=3")  # WARNING 레벨만 출력
        chrome_options.add_argument("--silent")
        
        try:
            # WebDriver Manager를 통한 자동 ChromeDriver 설치
            if HAS_WEBDRIVER_MANAGER:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                print("✅ ChromeDriverManager로 드라이버 설정 완료")
            else:
                # 기본 방식 (로컬에서)
                self.driver = webdriver.Chrome(options=chrome_options)
                print("✅ 기본 Chrome 드라이버 설정 완료")
            
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return True
            
        except Exception as e:
            print(f"❌ 드라이버 설정 실패: {e}")
            print("💡 Chrome 또는 ChromeDriver가 설치되어 있는지 확인하세요.")
            return False
    
    def login_tistory(self):
        """티스토리 로그인"""
        try:
            print("🔐 티스토리 로그인 중...")
            
            # 티스토리 로그인 페이지 접속
            self.driver.get("https://www.tistory.com/auth/login")
            time.sleep(5)  # 대기 시간 증가
            
            print(f"📍 현재 URL: {self.driver.current_url}")
            print(f"📄 페이지 제목: {self.driver.title}")
            
            # 이메일 입력 - 다양한 선택자 시도
            email_selectors = [
                (By.NAME, "loginId"),
                (By.ID, "loginId"),
                (By.CSS_SELECTOR, "input[name='loginId']"),
                (By.CSS_SELECTOR, "input[type='email']"),
                (By.CSS_SELECTOR, "input[placeholder*='이메일'], input[placeholder*='email']")
            ]
            
            email_input = None
            for selector_type, selector_value in email_selectors:
                try:
                    email_input = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((selector_type, selector_value))
                    )
                    print(f"✅ 이메일 입력창 찾음: {selector_type} = {selector_value}")
                    break
                except:
                    continue
            
            if not email_input:
                print("❌ 이메일 입력창을 찾을 수 없습니다.")
                return False
            
            email_input.clear()
            email_input.send_keys(self.email)
            time.sleep(1)
            
            # 비밀번호 입력 - 다양한 선택자 시도
            password_selectors = [
                (By.NAME, "password"),
                (By.ID, "password"),
                (By.CSS_SELECTOR, "input[name='password']"),
                (By.CSS_SELECTOR, "input[type='password']")
            ]
            
            password_input = None
            for selector_type, selector_value in password_selectors:
                try:
                    password_input = self.driver.find_element(selector_type, selector_value)
                    print(f"✅ 비밀번호 입력창 찾음: {selector_type} = {selector_value}")
                    break
                except:
                    continue
            
            if not password_input:
                print("❌ 비밀번호 입력창을 찾을 수 없습니다.")
                return False
                
            password_input.clear()
            password_input.send_keys(self.password)
            time.sleep(1)
            
            # 로그인 버튼 클릭 - 다양한 선택자 시도
            login_button_selectors = [
                "//button[@type='submit']",
                "//button[contains(text(), '로그인')]",
                "//input[@type='submit']",
                "//a[contains(text(), '로그인')]",
                "//*[@id='loginBtn']"
            ]
            
            login_clicked = False
            for button_xpath in login_button_selectors:
                try:
                    login_button = self.driver.find_element(By.XPATH, button_xpath)
                    login_button.click()
                    print(f"✅ 로그인 버튼 클릭: {button_xpath}")
                    login_clicked = True
                    break
                except:
                    continue
            
            if not login_clicked:
                print("❌ 로그인 버튼을 찾을 수 없습니다.")
                return False
            
            # 로그인 완료 대기 (더 길게)
            time.sleep(8)
            
            # 현재 상태 확인
            print(f"📍 로그인 후 URL: {self.driver.current_url}")
            print(f"📄 로그인 후 제목: {self.driver.title}")
            
            # 로그인 성공 확인 - 더 관대한 조건
            current_url = self.driver.current_url.lower()
            page_source = self.driver.page_source.lower()
            
            success_indicators = [
                "manage" in current_url,
                "blog" in current_url,
                "tistory.com" in current_url and "login" not in current_url,
                "관리" in page_source,
                "글쓰기" in page_source,
                "dashboard" in page_source
            ]
            
            if any(success_indicators):
                print("✅ 티스토리 로그인 성공!")
                return True
            else:
                print("❌ 로그인 실패 - 성공 지표를 찾을 수 없습니다.")
                print(f"   현재 URL: {current_url}")
                return False
                
        except Exception as e:
            print(f"❌ 로그인 오류: {e}")
            print(f"   현재 URL: {self.driver.current_url if self.driver else 'N/A'}")
            return False
    
    def write_post(self, title, content, tags=None, is_draft=True):
        """글 작성 및 임시저장"""
        try:
            print(f"📝 글 작성 중: {title[:30]}...")
            
            # 블로그 관리 페이지로 이동
            manage_url = f"{self.blog_url}/manage"
            self.driver.get(manage_url)
            time.sleep(2)
            
            # 글쓰기 버튼 클릭
            try:
                write_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'newpost') or contains(text(), '글쓰기')]"))
                )
                write_button.click()
            except:
                # 직접 URL로 이동
                self.driver.get(f"{self.blog_url}/manage/newpost/")
            
            time.sleep(3)
            
            # 제목 입력
            title_input = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder*='제목'], input[name*='title'], #title"))
            )
            title_input.clear()
            title_input.send_keys(title)
            
            time.sleep(1)
            
            # 본문 입력 (에디터 타입에 따라 다름)
            try:
                # HTML 에디터 시도
                self.driver.switch_to.frame(self.driver.find_element(By.TAG_NAME, "iframe"))
                content_area = self.driver.find_element(By.TAG_NAME, "body")
                content_area.clear()
                content_area.send_keys(content)
                self.driver.switch_to.default_content()
            except:
                try:
                    # 일반 textarea 시도
                    content_textarea = self.driver.find_element(By.CSS_SELECTOR, "textarea[name*='content'], #content, .editor-content")
                    content_textarea.clear()
                    content_textarea.send_keys(content)
                except:
                    print("⚠️ 본문 입력 영역을 찾을 수 없습니다.")
            
            time.sleep(1)
            
            # 태그 입력 (있는 경우)
            if tags:
                try:
                    tag_input = self.driver.find_element(By.CSS_SELECTOR, "input[placeholder*='태그'], input[name*='tag'], #tag")
                    tag_input.clear()
                    tag_input.send_keys(', '.join(tags))
                except:
                    print("⚠️ 태그 입력 영역을 찾을 수 없습니다.")
            
            time.sleep(1)
            
            # 임시저장 또는 발행
            if is_draft:
                # 임시저장 버튼 찾기
                save_buttons = [
                    "//button[contains(text(), '임시저장')]",
                    "//button[contains(text(), '저장')]",
                    "//input[@value='임시저장']",
                    "//a[contains(text(), '임시저장')]"
                ]
                
                saved = False
                for button_xpath in save_buttons:
                    try:
                        save_button = self.driver.find_element(By.XPATH, button_xpath)
                        save_button.click()
                        saved = True
                        break
                    except:
                        continue
                
                if not saved:
                    print("⚠️ 임시저장 버튼을 찾을 수 없어 일반 저장을 시도합니다.")
                    # 일반 저장/발행 버튼 시도
                    try:
                        publish_button = self.driver.find_element(By.XPATH, "//button[contains(text(), '발행') or contains(text(), '저장')]")
                        publish_button.click()
                    except:
                        print("❌ 저장 버튼을 찾을 수 없습니다.")
                        return False
            
            time.sleep(3)
            
            # 성공 확인
            if "manage" in self.driver.current_url or "성공" in self.driver.page_source:
                print(f"✅ 글 저장 성공: {title[:30]}...")
                return True
            else:
                print(f"❌ 글 저장 실패: {title[:30]}...")
                return False
                
        except Exception as e:
            print(f"❌ 글 작성 오류: {e}")
            return False
    
    def auto_post_articles(self, articles, headless=False):
        """여러 글 자동 포스팅"""
        if not articles:
            print("❌ 포스팅할 글이 없습니다.")
            return
        
        # 드라이버 설정
        if not self.setup_driver(headless=headless):
            return
        
        try:
            # 로그인
            if not self.login_tistory():
                return
            
            print(f"🚀 {len(articles)}개 글 자동 포스팅 시작...")
            
            success_count = 0
            fail_count = 0
            
            for i, article in enumerate(articles):
                try:
                    print(f"\n[{i+1}/{len(articles)}] 처리 중...")
                    
                    title = article.get('title', '제목 없음')
                    content = article.get('content', '')
                    tags = article.get('tags', ['AI재작성', '자동포스팅'])
                    
                    if self.write_post(title, content, tags, is_draft=True):
                        success_count += 1
                    else:
                        fail_count += 1
                    
                    # 랜덤 대기 (3-7초)
                    wait_time = random.uniform(3, 7)
                    time.sleep(wait_time)
                    
                except Exception as e:
                    print(f"❌ 글 처리 오류: {e}")
                    fail_count += 1
            
            print(f"\n📊 포스팅 완료!")
            print(f"✅ 성공: {success_count}개")
            print(f"❌ 실패: {fail_count}개")
            
            return success_count, fail_count
            
        finally:
            if self.driver:
                self.driver.quit()
                print("🔚 브라우저 종료")

def test_selenium_posting():
    """Selenium 포스팅 테스트"""
    poster = TistorySeleniumPoster()
    
    # 테스트 글
    test_articles = [
        {
            'title': 'Selenium 자동 포스팅 테스트',
            'content': '''이것은 Selenium을 이용한 자동 포스팅 테스트입니다.

## 주요 특징

- 웹 브라우저 자동화를 통한 포스팅
- 티스토리 임시저장 기능 지원
- API 없이도 안정적인 포스팅 가능

### 장점
1. API 제한 없음
2. 실제 사용자와 동일한 방식
3. 모든 기능 사용 가능

**참고**: 이 글은 자동으로 임시저장됩니다.''',
            'tags': ['Selenium', '자동포스팅', '테스트']
        }
    ]
    
    poster.auto_post_articles(test_articles, headless=False)

if __name__ == "__main__":
    test_selenium_posting()