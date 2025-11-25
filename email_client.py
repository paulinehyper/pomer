import imaplib
import email
from datetime import datetime, timedelta
from typing import List, Dict
from models import decode_mime_words, normalize_subject

def extract_text_from_message(msg: email.message.Message) -> str:
	parts = []
	if msg.is_multipart():
		for part in msg.walk():
			ctype = part.get_content_type()
			disp = str(part.get("Content-Disposition") or "")
			if ctype == "text/plain" and "attachment" not in disp:
				try:
					charset = part.get_content_charset() or "utf-8"
					text = part.get_payload(decode=True).decode(charset, errors="ignore")
					parts.append(text)
				except Exception:
					continue
	else:
		if msg.get_content_type() == "text/plain":
			try:
				charset = msg.get_content_charset() or "utf-8"
				text = msg.get_payload(decode=True).decode(charset, errors="ignore")
				parts.append(text)
			except Exception:
				pass
	return "".join(parts)

def fetch_emails(username: str, password: str, host: str, port: int, use_ssl: bool, days: int = 7) -> List[Dict]:
	imap = None
	try:
		if use_ssl:
			imap = imaplib.IMAP4_SSL(host, port)
		else:
			imap = imaplib.IMAP4(host, port)
		imap.login(username, password)
	except imaplib.IMAP4.error as e:
		raise imaplib.IMAP4.error(f"IMAP 로그인 실패: {e}")
	except Exception as e:
		raise Exception(f"IMAP 서버 연결 실패: {e}")
	imap.select("INBOX")
	since_date = (datetime.now() - timedelta(days=days)).strftime("%d-%b-%Y")
	status, data = imap.search(None, f'(SINCE {since_date})')
	if status != "OK":
		if imap:
			imap.logout()
		raise Exception(f"IMAP 검색 실패: {status}")
	emails: List[Dict] = []
	for num in reversed(data[0].split()):
		msg_id_num = num.decode()
		status, msg_data = imap.fetch(num, "(RFC822)")
		if status != "OK":
			continue
		raw = msg_data[0][1]
		msg = email.message_from_bytes(raw)
		subject = decode_mime_words(msg.get("Subject", ""))
		from_ = decode_mime_words(msg.get("From", ""))
		date_str = decode_mime_words(msg.get("Date", ""))
		body = extract_text_from_message(msg)
		normalized_subject = normalize_subject(subject)
		full_text = f"{(normalized_subject + ' ') * 3}{body}"
		emails.append({
			"msg_id": msg_id_num,
			"subject": subject,
			"subject_norm": normalized_subject,
			"from": from_,
			"date_header": date_str,
			"body": body,
			"full_text": full_text,
		})
	imap.close()
	imap.logout()
	return emails
# 이메일 수신 및 파싱 관련 함수/클래스

