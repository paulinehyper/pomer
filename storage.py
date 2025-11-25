# 카테고리 및 학습 데이터 저장/로드 함수
from typing import List
from models import DEFAULT_CATEGORIES

def load_categories() -> List[str]:
	categories = DEFAULT_CATEGORIES.copy()
	if os.path.exists(USER_CATEGORIES_FILE):
		try:
			with open(USER_CATEGORIES_FILE, "r", encoding="utf-8") as f:
				user_cats = json.load(f)
				for cat in user_cats:
					if cat not in categories:
						categories.append(cat)
		except:
			pass
	return categories

def save_categories(categories: List[str]):
	user_cats = [cat for cat in categories if cat not in DEFAULT_CATEGORIES]
	try:
		with open(USER_CATEGORIES_FILE, "w", encoding="utf-8") as f:
			json.dump(user_cats, f, indent=2, ensure_ascii=False)
	except Exception as e:
		raise Exception(f"카테고리 저장 실패: {e}")

def load_training_data() -> List[dict]:
	if os.path.exists(TRAINING_DATA_FILE):
		try:
			with open(TRAINING_DATA_FILE, "r", encoding="utf-8") as f:
				return json.load(f)
		except:
			pass
	return []

def save_training_data(data: List[dict]):
	try:
		with open(TRAINING_DATA_FILE, "w", encoding="utf-8") as f:
			json.dump(data, f, indent=2, ensure_ascii=False)
	except Exception as e:
		raise Exception(f"학습 데이터 저장 실패: {e}")
# 파일 경로 및 설정/데이터 저장 함수
import os
import json
from typing import Dict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(BASE_DIR, "mail_settings.json")
USER_CATEGORIES_FILE = os.path.join(BASE_DIR, "user_categories.json")
TRAINING_DATA_FILE = os.path.join(BASE_DIR, "training_data.json")

def load_settings() -> Dict:
	if os.path.exists(SETTINGS_FILE):
		try:
			with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
				return json.load(f)
		except:
			pass
	return {
		"mail_server": "KSD 메일",
		"custom_host": "",
		"custom_port": 993,
		"custom_ssl": True,
		"days_lookback": 7
	}

def save_settings(settings: Dict):
	try:
		with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
			json.dump(settings, f, indent=2, ensure_ascii=False)
	except Exception as e:
		raise Exception(f"설정 저장 실패: {e}")
# 설정 및 데이터 저장/로드 함수

