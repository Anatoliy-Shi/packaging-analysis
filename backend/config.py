"""Настройки проекта: пути, колонки, анонимизация, период."""

from dataclasses import dataclass
from datetime import date
from pathlib import Path


# --- Пути ---
BASE_DIR = Path(__file__).parent
PROJECT_ROOT = BASE_DIR.parent
FRONTEND_DATA = PROJECT_ROOT / "frontend" / "public" / "data"

INPUT_FILE = BASE_DIR / "12.xlsm"
SHEET_NAME = "Упаковка СУХОЙ КОРМ"

OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_FULL_DATA = OUTPUT_DIR / "полные_данные_объём_простой.csv"
OUTPUT_VOLUME_BY_SHIFT = OUTPUT_DIR / "объём_по_сменам.csv"
OUTPUT_DOWNTIME_BY_SHIFT = OUTPUT_DIR / "простой_по_сменам.csv"
OUTPUT_JSON = OUTPUT_DIR / "analytics.json"
OUTPUT_JSON_FRONTEND = FRONTEND_DATA / "analytics.json"


# --- Колонки Excel (индексы) ---
DATE_COL = 5
SHIFT_COL = 7
LINE_COL = 10
WEIGHT_COL = 27
DOWNTIME_COL = 58
PROBLEM_COL = 59
COMMENT_COL = 60

HEADER_MARKER = "УПАКОВАНО"


# --- Смены ---
SHIFT_MAP = {
    "Первая": 1,
    "Вторая": 2,
    "Третья": 3,
    "Четвертая": 4,
}


# --- Период по умолчанию ---
DATE_FROM: date | None = None
DATE_TO: date | None = None


# --- Анонимизация ---
ANONYMIZE = True
ANONYMIZE_SEED = 42
ANONYMIZE_RANGE = (0.85, 1.15)


# --- Прочее ---
try:
    import local_config  # noqa: F401
    from local_config import *  # noqa: F401, F403
    print("🔓 Локальный режим (реальные данные)")
except ImportError:
    print("🔒 Публичный режим (маскированные данные)")