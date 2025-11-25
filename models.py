# 카테고리, 키워드, 설명 등 상수 정의
import os
from datetime import datetime, timedelta, date
import re

MAIL_PRESETS = {
	"KSD 메일": {"host": "omail.ksd.or.kr", "port": 143, "use_ssl": False},
	"Gmail": {"host": "imap.gmail.com", "port": 993, "use_ssl": True},
	"Naver": {"host": "imap.naver.com", "port": 993, "use_ssl": True},
	"Outlook": {"host": "outlook.office365.com", "port": 993, "use_ssl": True},
	"Daum": {"host": "imap.daum.net", "port": 993, "use_ssl": True},
	"사용자 정의": {"host": "", "port": 993, "use_ssl": True}
}

DAYS_LOOKBACK = 7
REPLY_KEYWORDS = ["회신", "답장", "response", "reply", "제출", "보고"]
DUE_KEYWORDS = [
	"까지", "제출", "요청", "보고", "마감", "기한",
	"deadline", "due", "회신", "요망", "필요"
]
DEFAULT_CATEGORIES = ["제출", "안내", "검토", "광고"]
DEADLINE_RELATED_CATEGORIES = ["제출"]
CATEGORY_DESCRIPTIONS = {
	"제출": "답장/회신이 필요하고 제출 기한이 있는 메일",
	"안내": "정보 공유 및 가이드 메일 (답장 불필요)",
	"검토": "확인이 필요하지만 답장 기한이 없는 메일",
	"광고": "마케팅, 프로모션, 뉴스레터 등 홍보성 메일"
}

# 유틸리티 함수
def decode_mime_words(s: str) -> str:
	from email.header import decode_header
	if not s:
		return ""
	decoded_fragments = []
	for frag, enc in decode_header(s):
		if isinstance(frag, bytes):
			try:
				decoded_fragments.append(frag.decode(enc or "utf-8", errors="ignore"))
			except Exception:
				decoded_fragments.append(frag.decode("utf-8", errors="ignore"))
		else:
			decoded_fragments.append(frag)
	return "".join(decoded_fragments)

def normalize_subject(subject: str) -> str:
	if not subject:
		return ""
	subject = re.sub(r"\d{1,2}\s*월\s*\d{1,2}\s*일\s*\([^)]*\)", "", subject)
	subject = re.sub(r"\d{1,2}\s*월\s*\d{1,2}\s*일", "", subject)
	subject = re.sub(r"\d{1,2}[./-]\d{1,2}", "", subject)
	subject = re.sub(r"\s+", " ", subject)
	return subject.strip()

def extract_due_date_candidate(text: str) -> 'Optional[date]':
	if not text:
		return None
	now = datetime.now()
	this_year = now.year
	def is_valid(y, m, d):
		try:
			date(y, m, d)
			return True
		except:
			return False
	m = re.search(r"(\d{4})[.\-/](\d{1,2})[.\-/](\d{1,2})", text)
	if m:
		y, mo, d = map(int, m.groups())
		if is_valid(y, mo, d):
			return date(y, mo, d)
	m = re.search(r"(\d{1,2})\s*월\s*(\d{1,2})\s*일", text)
	if m:
		mo, d = map(int, m.groups())
		if is_valid(this_year, mo, d):
			due = date(this_year, mo, d)
			if due < now.date() and is_valid(this_year + 1, mo, d):
				due = date(this_year + 1, mo, d)
			return due
	m = re.search(r"(\d{1,2})[.\-/](\d{1,2})(?:\s|$|까지|[)\]])", text)
	if m:
		mo, d = map(int, m.groups())
		if is_valid(this_year, mo, d):
			due = date(this_year, mo, d)
			if due < now.date() and is_valid(this_year + 1, mo, d):
				due = date(this_year + 1, mo, d)
			return due
	return None

def calculate_days_remaining(due_date: date) -> tuple[int, str]:
	if not due_date:
		return 0, ""
	today = date.today()
	delta = (due_date - today).days
	if delta < 0:
		return delta, f"⚠️ {abs(delta)}일 경과"
	elif delta == 0:
		return delta, "🔴 오늘 마감"
	elif delta == 1:
		return delta, "🟡 내일 마감"
	elif delta <= 3:
		return delta, f"🟠 {delta}일 남음"
	elif delta <= 7:
		return delta, f"🟢 {delta}일 남음"
	else:
		return delta, f"{delta}일 남음"

# 데이터 구조 및 유틸 함수

