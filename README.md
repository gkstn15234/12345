# 티스토리 사이트맵 → HTML 자동 변환기

GitHub Actions를 통해 티스토리 사이트맵의 모든 entry 카테고리 글을 최적화된 HTML 파일로 자동 변환하는 프로젝트입니다.

## 🚀 주요 기능

- **자동화된 처리**: GitHub Actions를 통한 완전 자동화
- **티스토리 최적화**: 티스토리 블로그 구조에 최적화된 HTML 생성
- **반응형 디자인**: 모바일/데스크톱 모든 환경에서 최적 표시
- **SEO 최적화**: 메타 태그 및 Open Graph 태그 자동 생성
- **다크모드 지원**: 시스템 테마에 따른 자동 다크모드 전환

## 📁 파일 구조

```
├── .github/workflows/
│   └── sitemap-to-html.yml        # GitHub Actions 워크플로우
├── tistory_html_converter.py      # 메인 변환 스크립트
├── q.py                           # 기존 스크립트 (티스토리용으로 수정됨)
├── d.html                         # 티스토리 HTML 구조 참조파일
├── output/                        # 생성된 HTML 파일들
│   ├── index.html                 # 메인 인덱스 페이지
│   └── *.html                     # 변환된 개별 포스트들
└── README.md                      # 이 파일
```

## 🔧 설정 방법

### 1. GitHub Repository 설정

1. 이 저장소를 GitHub에 업로드
2. Settings → Actions → General에서 "Allow all actions" 선택
3. Settings → Pages에서 GitHub Pages 활성화 (Source: GitHub Actions)

### 2. 자동 실행 설정

GitHub Actions는 다음과 같이 실행됩니다:

- **매일 자동 실행**: 한국시간 오전 9시 (UTC 0시)
- **수동 실행**: Repository → Actions → "Sitemap to HTML Converter" → "Run workflow"
- **코드 푸시**: main 브랜치에 푸시할 때마다

### 3. 사이트맵 URL 변경

`tistory_html_converter.py` 파일에서 사이트맵 URL을 변경할 수 있습니다:

```python
def __init__(self):
    self.sitemap_url = "https://your-blog.tistory.com/sitemap.xml"  # 여기를 수정
```

## 📊 처리 과정

1. **사이트맵 다운로드**: 티스토리 사이트맵 XML 파일 가져오기
2. **URL 추출**: `/entry/` 경로가 포함된 포스트 URL만 필터링
3. **콘텐츠 추출**: 각 포스트에서 제목, 내용, 이미지, 날짜 추출
4. **HTML 생성**: 티스토리 최적화된 HTML 템플릿으로 변환
5. **인덱스 생성**: 모든 포스트를 나열하는 메인 페이지 생성
6. **GitHub Pages 배포**: 자동으로 웹사이트로 배포

## 🎨 HTML 특징

### 디자인 특징
- **모던한 UI**: 깔끔하고 현대적인 디자인
- **그라디언트 배경**: 시각적으로 매력적인 배경
- **카드형 레이아웃**: 각 포스트를 카드 형태로 표시
- **호버 효과**: 마우스 오버 시 부드러운 애니메이션

### 기술적 특징
- **시맨틱 HTML**: 검색엔진 최적화
- **CSS Grid/Flexbox**: 반응형 레이아웃
- **Progressive Enhancement**: 점진적 향상
- **Web Standards**: 웹 표준 준수

## 🔍 사용 예시

### 로컬에서 테스트 실행

```bash
# 필요한 패키지 설치
pip install requests beautifulsoup4 lxml

# 스크립트 실행
python tistory_html_converter.py
```

### 생성된 파일 확인

```bash
# output 디렉토리에서 파일 확인
ls output/

# 브라우저에서 결과 확인
open output/index.html  # macOS
start output/index.html # Windows
```

## 📈 모니터링

GitHub Actions 실행 현황은 다음에서 확인할 수 있습니다:

- Repository → Actions 탭
- 각 워크플로우 실행 로그 확인
- 성공/실패 상태 및 에러 메시지 확인

## 🛠 커스터마이징

### CSS 스타일 변경

`tistory_html_converter.py`의 `create_tistory_optimized_html` 메서드에서 CSS를 수정할 수 있습니다.

### HTML 구조 변경

같은 메서드에서 HTML 템플릿을 원하는 대로 수정할 수 있습니다.

### 추가 메타데이터

`extract_tistory_content` 메서드에서 더 많은 정보를 추출하도록 수정할 수 있습니다.

## 🔧 문제 해결

### 자주 발생하는 문제들

1. **사이트맵 접근 실패**
   - 해결: 사이트맵 URL이 올바른지 확인
   - 해결: 블로그가 공개 상태인지 확인

2. **콘텐츠 추출 실패**  
   - 해결: 티스토리 테마의 클래스명이 변경되었을 수 있음
   - 해결: `content_selectors` 리스트에 새로운 선택자 추가

3. **GitHub Actions 실행 실패**
   - 해결: Actions 로그를 확인하여 에러 메시지 확인
   - 해결: 권한 설정이 올바른지 확인

## 📋 TODO

- [ ] 이미지 최적화 (WebP 변환)
- [ ] RSS 피드 생성
- [ ] 검색 기능 추가
- [ ] 태그 기반 필터링
- [ ] 더 많은 티스토리 테마 지원

## 📄 라이선스

MIT License - 자유롭게 사용, 수정, 배포 가능합니다.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

**💡 Tip**: GitHub Pages로 배포된 사이트는 `https://your-username.github.io/repository-name` 에서 확인할 수 있습니다.