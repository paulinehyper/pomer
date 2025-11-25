import re
from datetime import datetime
from typing import List, Dict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
try:
	from sentence_transformers import SentenceTransformer
	SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
	SENTENCE_TRANSFORMERS_AVAILABLE = False
from storage import load_categories, load_training_data, save_training_data


class EmailClassifier:
	def __init__(self):
		self.use_embeddings = SENTENCE_TRANSFORMERS_AVAILABLE
		if self.use_embeddings:
			try:
				print("한국어 임베딩 모델 로딩 중...")
				self.embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
				self.classifier = SVC(kernel='rbf', probability=True, random_state=42)
				print("✓ 한국어 임베딩 모델 로딩 완료")
			except Exception as e:
				print(f"임베딩 모델 로드 실패, TF-IDF 사용: {e}")
				self.use_embeddings = False
		if not self.use_embeddings:
			self.vectorizer = TfidfVectorizer(max_features=500, ngram_range=(1, 2))
			self.classifier = RandomForestClassifier(n_estimators=100, random_state=42)
		self.is_trained = False
		self.categories = load_categories()
		self.training_data = load_training_data()

	def preprocess_text(self, text: str) -> str:
		text = re.sub(r'[^\w\s가-힣]', ' ', text)
		text = re.sub(r'\s+', ' ', text)
		return text.strip()

	def train(self):
		if len(self.training_data) < 3:
			return False
		texts = []
		labels = []
		for item in self.training_data:
			text = f"{item['subject']} {item['body']}"
			texts.append(self.preprocess_text(text))
			labels.append(item['category'])
		try:
			if self.use_embeddings:
				X = self.embedding_model.encode(texts, show_progress_bar=False)
			else:
				X = self.vectorizer.fit_transform(texts)
			self.classifier.fit(X, labels)
			self.is_trained = True
			return True
		except Exception as e:
			print(f"학습 실패: {e}")
			return False

	def predict(self, subject: str, body: str, from_email: str = "") -> str:
		from_email_lower = from_email.lower()
		social_media_domains = [
			"linkedin", "facebook", "twitter", "instagram", "tiktok",
			"youtube", "snapchat", "reddit", "pinterest", 
			"mail.instagram.com", "facebookmail.com", "linkedin.com"
		]
		if from_email_lower:
			for domain in social_media_domains:
				if domain in from_email_lower:
					return "광고"
		if not self.is_trained:
			return self.keyword_based_classify(subject, body, from_email)
		try:
			text = f"{subject} {body}"
			text = self.preprocess_text(text)
			if self.use_embeddings:
				X = self.embedding_model.encode([text], show_progress_bar=False)
			else:
				X = self.vectorizer.transform([text])
			prediction = self.classifier.predict(X)[0]
			probabilities = self.classifier.predict_proba(X)[0]
			max_prob = max(probabilities)
			if max_prob < 0.5:
				keyword_result = self.keyword_based_classify(subject, body, from_email)
				if keyword_result:
					return keyword_result
			return prediction
		except Exception as e:
			print(f"예측 실패: {e}")
			return self.keyword_based_classify(subject, body, from_email)

	def keyword_based_classify(self, subject: str, body: str, from_email: str = "") -> str:
		text = f"{subject} {body}".lower()
		from_email_lower = from_email.lower()
		social_media_domains = [
			"linkedin", "facebook", "twitter", "instagram", "tiktok",
			"youtube", "snapchat", "reddit", "pinterest", "카카오", "네이버밴드",
			"mail.instagram.com", "facebookmail.com", "linkedin.com"
		]
		social_notification_patterns = [
			"업데이트 공유", "님이 최근 올렸음", "님이 올렸음", "반응", "댓글", "좋아요",
			"팔로우", "추천", "회원님을 위한", "추천 피드", "새로운 게시물", "님이 공유",
			"shared an update", "posted", "likes", "comments", "followers",
			"new connection", "직원이", "인맥들의", "스토리", "story", "stories",
			"확인해보세요", "새로운 알림", "new notification"
		]
		if from_email_lower:
			for domain in social_media_domains:
				if domain in from_email_lower:
					return "광고"
		is_social_media = any(domain in text for domain in social_media_domains)
		has_social_notification = any(pattern in text for pattern in social_notification_patterns)
		if is_social_media:
			if has_social_notification or "noreply" in text or "no-reply" in text:
				return "광고"
		auto_mail_patterns = [
			"발신전용", "noreply", "no-reply", "no_reply", "account_noreply",
			"자동발송", "자동전송", "do not reply", "본 메일은 발신전용",
			"updates-noreply", "notification", "이메일 받지 않기", "구독 취소"
		]
		if any(pattern in text for pattern in auto_mail_patterns):
			return "안내"
		system_patterns = [
			"비밀번호 생성", "인증", "로그인", "계정", "보안",
			"생성되었습니다", "변경되었습니다", "등록되었습니다",
			"password", "authentication", "verification"
		]
		system_score = sum(1 for pattern in system_patterns if pattern in text)
		submit_keywords = [
			"제출", "회신", "답장", "응답", "reply", "보내주세요", "제출해주",
			"요청드립니다", "부탁드립니다", "회신해주", "보내주시기"
		]
		ad_keywords = [
			"광고", "프로모션", "할인", "이벤트", "특가", "세일", "쿠폰",
			"promotion", "discount", "sale", "offer", "deal", "뉴스레터",
			"마케팅", "unsubscribe", "이메일 받지 않기", "구독 취소",
			"업데이트 공유", "추천", "더보기", "linkedin", "updates-noreply",
			"반응", "댓글", "좋아요", "공감", "newsletter",
			"지금 뜨는", "바로 확인", "놓치지 마세요", "채용", "포지션",
			"경력직", "신입", "채용정보", "구인", "지원하세요", "합격",
			"취업", "이력서", "Job", "Career", "Hiring"
		]
		guide_keywords = [
			"안내", "알림", "공지", "공유", "참고", "information", "notice",
			"알려드립니다", "안내드립니다", "공지사항", "소식",
			"발송되었습니다", "생성 내역", "활동 내역"
		]
		review_keywords = [
			"검토", "확인", "review", "점검", "살펴", "검토해", "확인해",
			"의견", "피드백", "논의"
		]
		submit_score = sum(1 for kw in submit_keywords if kw in text)
		ad_score = sum(1 for kw in ad_keywords if kw in text)
		guide_score = sum(1 for kw in guide_keywords if kw in text)
		review_score = sum(1 for kw in review_keywords if kw in text)
		ad_patterns = [
			"unsubscribe", "이메일 받지 않기", "구독 취소", "수신거부",
			"updates-noreply", "newsletter", "marketing"
		]
		if any(pattern in text for pattern in ad_patterns):
			ad_score += 3
		social_media_list = ["linkedin", "facebook", "instagram", "twitter", "youtube", "tiktok", "reddit"]
		social_notification_words = ["업데이트", "공유", "반응", "댓글", "좋아요", "팔로우", "추천", "포스트", "님이"]
		is_from_social = any(social in text for social in social_media_list)
		has_notification = any(word in text for word in social_notification_words)
		if is_from_social and has_notification:
			ad_score += 5
		if system_score >= 2:
			guide_score += 3
		submit_request_patterns = [
			r'제출해\s*주', r'회신해\s*주', r'보내\s*주', r'답장\s*부탁',
			r'요청드립니다', r'제출\s*요청'
		]
		has_submit_request = any(re.search(pattern, text) for pattern in submit_request_patterns)
		has_deadline = re.search(r'\d{1,2}[월/.-]\d{1,2}[일]?\s*(까지|by|before)|까지\s*제출|마감|기한|deadline', text)
		if has_deadline and has_submit_request:
			submit_score += 3
		elif has_deadline:
			review_score += 1
		scores = {
			"제출": submit_score,
			"광고": ad_score,
			"안내": guide_score,
			"검토": review_score
		}
		max_category = max(scores, key=scores.get)
		if scores[max_category] == 0:
			return "안내"
		return max_category

	def add_training_data(self, subject: str, body: str, category: str):
		self.training_data.append({
			"subject": subject,
			"body": body[:500],
			"category": category,
			"timestamp": datetime.now().isoformat()
		})
		if len(self.training_data) > 1000:
			self.training_data = self.training_data[-1000:]
		save_training_data(self.training_data)
		self.train()
# AI/키워드 분류 관련 클래스 및 함수

