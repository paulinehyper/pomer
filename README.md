# 📧 AI Email Manager

**AI 기반 이메일 관리 및 To-Do 시스템**

한국어를 지원하는 AI 모델을 사용하여 이메일을 자동으로 분류하고, 마감일을 추출하며, 할일 목록을 관리하는 스마트한 이메일 관리 프로그램입니다.

## ✨ 주요 기능

### 🤖 3단계 하이브리드 AI 분류
1. **발신자 주소 분석** - 소셜미디어/스팸 즉시 차단
2. **AI 의미 분석** - Sentence Transformers로 문맥 이해
3. **키워드 보완** - 낮은 신뢰도일 때 규칙 기반 보완

### 📊 4가지 자동 분류
- **제출** - 기한이 있는 제출 요청 메일
- **안내** - 정보 공유, 공지사항
- **검토** - 확인이 필요한 메일
- **광고** - 마케팅, SNS 알림, 채용 정보

### 📅 스마트 마감일 관리
- 다양한 날짜 형식 자동 인식 (YYYY-MM-DD, MM월 DD일, MM/DD)
- 남은 일수 계산 및 시각적 표시 (🔴 긴급 / 🟠 곧 마감 / 🟢 여유)
- 마감일 기준 자동 정렬

### ✅ To-Do 리스트
- 제출/검토 메일만 필터링
- 완료/미완료 상태 관리
- 기한 경과 항목 자동 표시
- 통계 대시보드 (미완료/완료/기한경과)

### 📧 멀티 메일 서버 지원
- **KSD** (omail.ksd.or.kr)
- **Gmail** (imap.gmail.com)
- **Naver** (imap.naver.com)
- **Outlook** (outlook.office365.com)
- **Daum** (imap.daum.net)
- **Custom** (사용자 정의 설정)

## 🚀 설치 및 실행

### 요구사항
- Python 3.8 이상

### 설치
```bash
# 저장소 클론
git clone https://github.com/your-username/ai-email-manager.git
cd ai-email-manager

# 가상환경 생성 및 활성화
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Mac/Linux

# 필요한 패키지 설치
pip install sentence-transformers torch scikit-learn
```

### 실행
```bash
python 3.py
```

## 🎯 사용 방법

1. **로그인**
   - 메일 서버 선택 (또는 사용자 정의)
   - 계정 정보 입력
   - 조회 기간 설정 (기본 7일)

2. **설정**
   - 상단 메뉴의 "설정" 버튼 클릭
   - 메일 서버 변경 가능
   - 조회 기간 조정

3. **메일 분류**
   - AI가 자동으로 4가지 카테고리로 분류
   - 잘못 분류된 메일은 드롭다운으로 수정 가능
   - 수정할 때마다 AI가 학습하여 정확도 향상

4. **To-Do 관리**
   - "할일" 탭에서 제출/검토 메일만 확인
   - 체크박스로 완료/미완료 상태 변경
   - 마감일 순으로 자동 정렬

## 🧠 AI 모델

### 한국어 특화 모델
- **sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2**
  - 다국어 지원 (한국어 포함)
  - 경량화된 모델 (빠른 처리 속도)
  - 문맥 기반 의미 이해

### 학습 방식
- 사용자가 메일을 분류/수정할 때마다 자동 학습
- 최대 1000개의 학습 데이터 보관
- SVM 또는 Random Forest 분류기 사용

## 📁 파일 구조

```
mymail/
├── 3.py                      # 메인 프로그램
├── .gitignore               # Git 제외 파일
├── README.md                # 이 파일
├── mail_settings.json       # 메일 설정 (자동 생성)
├── user_categories.json     # 사용자 카테고리 (자동 생성)
├── training_data.json       # AI 학습 데이터 (자동 생성)
└── *.pkl                    # 학습된 모델 (자동 생성)
```

## 🔒 보안

- 메일 계정 정보는 로컬에만 저장 (`mail_settings.json`)
- 민감한 정보는 `.gitignore`에 포함되어 Git에 업로드되지 않음
- IMAP SSL 연결 지원

## 🛠 기술 스택

- **GUI**: tkinter
- **AI/ML**: sentence-transformers, scikit-learn, torch
- **이메일**: imaplib (IMAP4, IMAP4_SSL)
- **한국어 처리**: konlpy (선택 사항)

## 📝 라이선스

MIT License

## 👨‍💻 개발자

개발 문의 및 버그 리포트는 Issues에 등록해주세요.

---

**Made with ❤️ and AI**
