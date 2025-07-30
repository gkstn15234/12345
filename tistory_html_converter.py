#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
티스토리 사이트맵을 최적화된 HTML로 변환하는 자동화 스크립트
GitHub Actions에서 실행됩니다.
"""

import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import os
import json
from datetime import datetime
import re
import time
import random

class TistorySitemapConverter:
    def __init__(self):
        self.sitemap_url = "https://difks2004.tistory.com/sitemap.xml"
        self.output_dir = "output"
        self.processed_urls = set()
        
        # 출력 디렉토리 생성
        os.makedirs(self.output_dir, exist_ok=True)
        
    def fetch_sitemap(self):
        """사이트맵 XML 가져오기"""
        print("🌐 사이트맵 다운로드 중...")
        try:
            response = requests.get(self.sitemap_url, timeout=30)
            response.raise_for_status()
            print(f"✅ 사이트맵 다운로드 완료: {len(response.text):,} bytes")
            return response.text
        except Exception as e:
            print(f"❌ 사이트맵 다운로드 실패: {e}")
            return None
    
    def parse_sitemap_urls(self, sitemap_content):
        """사이트맵에서 모든 entry URL 추출"""
        urls = []
        try:
            # XML 파싱
            root = ET.fromstring(sitemap_content)
            
            # 네임스페이스 처리
            namespaces = {
                '': 'http://www.sitemaps.org/schemas/sitemap/0.9'
            }
            
            for url_elem in root.findall('.//url', namespaces):
                loc_elem = url_elem.find('loc', namespaces)
                lastmod_elem = url_elem.find('lastmod', namespaces)
                
                if loc_elem is not None:
                    url = loc_elem.text
                    lastmod = lastmod_elem.text if lastmod_elem is not None else None
                    
                    # entry 카테고리만 처리 (포스트 URL)
                    if url and '/entry/' in url:
                        urls.append({
                            'url': url,
                            'lastmod': lastmod
                        })
                        
        except Exception as e:
            print(f"⚠️ XML 파싱 오류: {e}")
            # 대안적 파싱 방법
            lines = sitemap_content.split('\n')
            for line in lines:
                if '<loc>' in line and '</loc>' in line:
                    start = line.find('<loc>') + 5
                    end = line.find('</loc>')
                    if start > 4 and end > start:
                        url = line[start:end]
                        if '/entry/' in url:
                            urls.append({
                                'url': url,
                                'lastmod': None
                            })
        
        print(f"📄 총 {len(urls)}개의 entry URL 발견")
        return urls
    
    def extract_tistory_content(self, url):
        """티스토리 개별 포스트에서 콘텐츠 추출"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 티스토리 제목 추출
            title = None
            title_selectors = [
                'h1.title_post',
                'h1.post-title',
                '.title_post',
                'h1',
                'title'
            ]
            
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    title = title_elem.get_text().strip()
                    break
            
            if not title:
                title = "제목 없음"
            
            # 티스토리 본문 내용 추출
            content = ""
            content_selectors = [
                '.entry-content',
                '.article_view',
                '.post-content',
                '.contents_style',
                '.post_ct'
            ]
            
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    # 광고, 스크립트 등 제거
                    for unwanted in content_elem.select('script, style, ins.adsbygoogle, .revenue_unit_wrap, .google-auto-placed'):
                        unwanted.decompose()
                    
                    # 티스토리 광고 div 제거
                    for ad_div in content_elem.find_all('div'):
                        if ad_div.get('data-tistory-react-app'):
                            ad_div.decompose()
                    
                    content = content_elem.get_text().strip()
                    break
            
            # 날짜 추출
            date = None
            date_selectors = [
                '.date',
                '.post-date',
                '.entry-date',
                'time'
            ]
            
            for selector in date_selectors:
                date_elem = soup.select_one(selector)
                if date_elem:
                    date = date_elem.get_text().strip()
                    break
            
            # 이미지 추출
            images = []
            if content_elem:
                for img in content_elem.find_all('img'):
                    img_src = img.get('src')
                    if img_src:
                        # 상대 URL을 절대 URL로 변환
                        if img_src.startswith('//'):
                            img_src = 'https:' + img_src
                        elif img_src.startswith('/'):
                            img_src = 'https://difks2004.tistory.com' + img_src
                        elif not img_src.startswith('http'):
                            img_src = 'https://difks2004.tistory.com/' + img_src
                        images.append(img_src)
            
            return {
                'title': title,
                'content': content,
                'date': date,
                'url': url,
                'images': images
            }
            
        except Exception as e:
            print(f"⚠️ 콘텐츠 추출 실패 ({url}): {e}")
            return None
    
    def create_tistory_optimized_html(self, post_data):
        """티스토리 최적화 HTML 구조 생성"""
        title = post_data['title']
        content = post_data['content']
        date = post_data['date'] or datetime.now().strftime('%Y.%m.%d')
        url = post_data['url']
        images = post_data.get('images', [])
        
        # 파일명 생성 (안전한 파일명으로 변환)
        safe_title = re.sub(r'[^\w\s-]', '', title)
        safe_title = re.sub(r'[-\s]+', '-', safe_title)
        filename = safe_title[:50] + '.html'
        
        # 메인 이미지 (첫 번째 이미지)
        main_image = images[0] if images else None
        
        html_template = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{content[:150]}...">
    <meta name="keywords" content="티스토리, 블로그, {title}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{content[:150]}...">
    <meta property="og:type" content="article">
    <meta property="og:url" content="{url}">
    {f'<meta property="og:image" content="{main_image}">' if main_image else ''}
    <title>{title}</title>
    
    <!-- 티스토리 최적화 CSS -->
    <style>
        body {{
            font-family: 'Malgun Gothic', '맑은 고딕', AppleSDGothicNeo, 'Apple SD Gothic Neo', sans-serif;
            line-height: 1.7;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
            color: #333;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        }}
        .post-header {{
            border-bottom: 3px solid #007bff;
            padding-bottom: 25px;
            margin-bottom: 35px;
        }}
        .post-title {{
            font-size: 2.4em;
            font-weight: 700;
            color: #1a1a1a;
            margin-bottom: 15px;
            line-height: 1.3;
            word-break: keep-all;
        }}
        .post-meta {{
            color: #6c757d;
            font-size: 0.95em;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        .post-meta span {{
            background: #f8f9fa;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9em;
        }}
        .main-image {{
            width: 100%;
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            margin: 25px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .post-content {{
            font-size: 1.15em;
            color: #333;
            line-height: 1.8;
            margin-bottom: 30px;
        }}
        .post-content p {{
            margin-bottom: 1.8em;
            word-break: keep-all;
        }}
        .post-content h3 {{
            color: #007bff;
            font-size: 1.4em;
            margin: 30px 0 15px 0;
            padding-bottom: 8px;
            border-bottom: 2px solid #e9ecef;
        }}
        .post-content blockquote {{
            background: #f8f9fa;
            border-left: 4px solid #007bff;
            padding: 20px;
            margin: 25px 0;
            border-radius: 4px;
            font-style: italic;
        }}
        .source-link {{
            margin-top: 40px;
            padding: 25px;
            background: linear-gradient(135deg, #007bff, #0056b3);
            border-radius: 8px;
            text-align: center;
        }}
        .source-link a {{
            color: white;
            text-decoration: none;
            font-weight: bold;
            font-size: 1.1em;
            display: inline-block;
            padding: 10px 25px;
            background: rgba(255,255,255,0.2);
            border-radius: 25px;
            transition: all 0.3s ease;
        }}
        .source-link a:hover {{
            background: rgba(255,255,255,0.3);
            transform: translateY(-2px);
        }}
        .tag-list {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e9ecef;
        }}
        .tag {{
            display: inline-block;
            background: #e9ecef;
            color: #495057;
            padding: 5px 12px;
            border-radius: 15px;
            font-size: 0.9em;
            margin: 5px 5px 5px 0;
            text-decoration: none;
            transition: all 0.3s ease;
        }}
        .tag:hover {{
            background: #007bff;
            color: white;
        }}
        
        /* 반응형 디자인 */
        @media (max-width: 768px) {{
            body {{
                padding: 15px;
            }}
            .container {{
                padding: 25px;
            }}
            .post-title {{
                font-size: 2em;
            }}
            .post-content {{
                font-size: 1.1em;
            }}
            .post-meta {{
                flex-direction: column;
                align-items: flex-start;
                gap: 8px;
            }}
        }}
        
        /* 다크모드 지원 */
        @media (prefers-color-scheme: dark) {{
            body {{
                background-color: #1a1a1a;
                color: #e9ecef;
            }}
            .container {{
                background: #2d3748;
                color: #e9ecef;
            }}
            .post-title {{
                color: #f8f9fa;
            }}
            .post-content h3 {{
                color: #4dabf7;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="post-header">
            <h1 class="post-title">{title}</h1>
            <div class="post-meta">
                <span>📅 {date}</span>
                <span>👤 difks2004</span>
                <span>🔗 <a href="{url}" target="_blank" style="color: #007bff; text-decoration: none;">원문 보기</a></span>
            </div>
        </div>
        
        {f'<img src="{main_image}" alt="{title}" class="main-image">' if main_image else ''}
        
        <div class="post-content">
            {self.format_content_for_html(content)}
        </div>
        
        <div class="tag-list">
            <a href="#" class="tag">티스토리</a>
            <a href="#" class="tag">블로그</a>
            <a href="#" class="tag">정보</a>
        </div>
        
        <div class="source-link">
            <a href="{url}" target="_blank">➡️ 원문에서 전체 내용 보기</a>
        </div>
    </div>
    
    <!-- 티스토리 최적화 스크립트 -->
    <script>
        // 외부 링크 새 창으로 열기
        document.querySelectorAll('a[href^="http"]').forEach(link => {{
            if (!link.href.includes(window.location.hostname)) {{
                link.target = '_blank';
                link.rel = 'noopener noreferrer';
            }}
        }});
        
        // 이미지 지연 로딩
        if ('IntersectionObserver' in window) {{
            const imageObserver = new IntersectionObserver((entries, observer) => {{
                entries.forEach(entry => {{
                    if (entry.isIntersecting) {{
                        const img = entry.target;
                        if (img.dataset.src) {{
                            img.src = img.dataset.src;
                            img.classList.remove('lazy');
                            imageObserver.unobserve(img);
                        }}
                    }}
                }});
            }});
            
            document.querySelectorAll('img[data-src]').forEach(img => {{
                imageObserver.observe(img);
            }});
        }}
        
        // 스무스 스크롤
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
            anchor.addEventListener('click', function (e) {{
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {{
                    target.scrollIntoView({{
                        behavior: 'smooth',
                        block: 'start'
                    }});
                }}
            }});
        }});
    </script>
</body>
</html>'''
        
        return html_template, filename
    
    def format_content_for_html(self, content):
        """콘텐츠를 HTML 형식으로 포맷팅"""
        if not content:
            return "<p>내용을 불러올 수 없습니다.</p>"
        
        # 문단 나누기
        paragraphs = content.split('\n\n')
        formatted_paragraphs = []
        
        for para in paragraphs:
            para = para.strip()
            if para:
                # 기본 HTML 태그 적용
                if len(para) > 100:  # 긴 문단은 일반 문단으로
                    para = f"<p>{para}</p>"
                elif para.startswith('•') or para.startswith('-'):  # 리스트 아이템
                    para = f"<li>{para[1:].strip()}</li>"
                else:  # 짧은 문단은 강조
                    para = f"<h3>{para}</h3>" if len(para) < 50 else f"<p><strong>{para}</strong></p>"
                
                formatted_paragraphs.append(para)
        
        # 리스트 태그로 감싸기
        formatted_content = '\n'.join(formatted_paragraphs)
        formatted_content = re.sub(r'(<li>.*?</li>)', r'<ul>\1</ul>', formatted_content, flags=re.DOTALL)
        
        return formatted_content
    
    def process_all_posts(self):
        """모든 포스트 처리"""
        print("🚀 티스토리 사이트맵 → HTML 변환 시작")
        
        # 사이트맵 가져오기
        sitemap_content = self.fetch_sitemap()
        if not sitemap_content:
            print("❌ 사이트맵을 가져올 수 없습니다.")
            return
        
        # URL 추출
        urls = self.parse_sitemap_urls(sitemap_content)
        if not urls:
            print("❌ URL을 찾을 수 없습니다.")
            return
        
        print(f"📝 {len(urls)}개 포스트 처리 시작...")
        
        processed = 0
        failed = 0
        
        for i, url_data in enumerate(urls):
            url = url_data['url']
            print(f"[{i+1}/{len(urls)}] 처리 중: {url}")
            
            # 콘텐츠 추출
            post_data = self.extract_tistory_content(url)
            
            if post_data:
                # HTML 생성
                html_content, filename = self.create_tistory_optimized_html(post_data)
                
                # 파일 저장
                filepath = os.path.join(self.output_dir, filename)
                
                # 파일명 중복 방지
                counter = 1
                while os.path.exists(filepath):
                    name, ext = os.path.splitext(filename)
                    filepath = os.path.join(self.output_dir, f"{name}-{counter}{ext}")
                    counter += 1
                
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    
                    processed += 1
                    print(f"✅ 생성완료: {os.path.basename(filepath)}")
                    
                except Exception as e:
                    print(f"❌ 파일 저장 실패: {e}")
                    failed += 1
            else:
                failed += 1
                print(f"❌ 콘텐츠 추출 실패: {url}")
            
            # API 제한 고려 (1-2초 대기)
            time.sleep(random.uniform(1, 2))
        
        # 인덱스 HTML 생성
        self.create_index_html(processed, failed)
        
        print(f"\n📊 처리 완료!")
        print(f"✅ 성공: {processed}개")
        print(f"❌ 실패: {failed}개")
        print(f"📁 출력 디렉토리: {self.output_dir}")
    
    def create_index_html(self, processed, failed):
        """인덱스 HTML 파일 생성"""
        # 생성된 HTML 파일 목록
        html_files = [f for f in os.listdir(self.output_dir) if f.endswith('.html')]
        
        index_html = f'''<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>티스토리 포스트 아카이브</title>
    <style>
        body {{
            font-family: 'Malgun Gothic', '맑은 고딕', AppleSDGothicNeo, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #667eea;
            padding-bottom: 30px;
            margin-bottom: 40px;
        }}
        .header h1 {{
            color: #333;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 25px;
            margin-bottom: 40px;
        }}
        .stat-box {{
            text-align: center;
            padding: 25px;
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            border-radius: 12px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        .stat-box h3 {{
            margin: 0 0 10px 0;
            font-size: 1.2em;
        }}
        .stat-box p {{
            margin: 0;
            font-size: 2em;
            font-weight: bold;
        }}
        .file-list {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }}
        .file-item {{
            padding: 20px;
            border: 2px solid #e9ecef;
            border-radius: 12px;
            background: #f8f9fa;
            transition: all 0.3s ease;
        }}
        .file-item:hover {{
            border-color: #667eea;
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        }}
        .file-item a {{
            color: #333;
            text-decoration: none;
            font-weight: bold;
            font-size: 1.1em;
            display: block;
        }}
        .file-item a:hover {{
            color: #667eea;
        }}
        .update-time {{
            color: #6c757d;
            font-size: 0.9em;
            text-align: center;
            margin-top: 30px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏠 티스토리 포스트 아카이브</h1>
            <p>자동 생성된 HTML 파일 목록</p>
        </div>
        
        <div class="stats">
            <div class="stat-box">
                <h3>✅ 성공</h3>
                <p>{processed}</p>
            </div>
            <div class="stat-box">
                <h3>❌ 실패</h3>
                <p>{failed}</p>
            </div>
            <div class="stat-box">
                <h3>📁 총 파일</h3>
                <p>{len(html_files)}</p>
            </div>
        </div>
        
        <div class="file-list">
'''
        
        for filename in sorted(html_files):
            if filename != 'index.html':
                title = filename.replace('.html', '').replace('-', ' ')
                index_html += f'''
            <div class="file-item">
                <a href="{filename}">{title}</a>
            </div>
'''
        
        index_html += f'''
        </div>
        
        <div class="update-time">
            <p><small>마지막 업데이트: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}</small></p>
        </div>
    </div>
</body>
</html>'''
        
        # 인덱스 파일 저장
        with open(os.path.join(self.output_dir, 'index.html'), 'w', encoding='utf-8') as f:
            f.write(index_html)
        
        print("📋 인덱스 파일 생성 완료: index.html")

def main():
    """메인 실행 함수"""
    converter = TistorySitemapConverter()
    converter.process_all_posts()

if __name__ == "__main__":
    main()