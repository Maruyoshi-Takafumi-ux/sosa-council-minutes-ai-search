"""
設定ファイル
.env に GEMINI_API_KEY を書いて使用してください
"""

import os
from dotenv import load_dotenv

load_dotenv()

# --- 対象サイト ---
BASE_URL = "https://ssp.kaigiroku.net"
TENANT = "sosa"
TENANT_ID = 212
TOP_URL = f"{BASE_URL}/tenant/{TENANT}/SpTop.html"
MINUTE_VIEW_URL = f"{BASE_URL}/tenant/{TENANT}/SpMinuteView.html"

# --- 収集対象年度 ---
# 匝瑳市は平成22年(2010)以前から公開されている（確認済み: 平成22年〜）。収集開始年は START_YEAR で調整する。
# 新年度が公開されたら LATEST_YEAR を更新するだけでよい（他ファイルは全てここを参照）。
START_YEAR = int(os.getenv("START_YEAR", "2023"))   # 令和5年〜（4年分。遡る場合は環境変数で指定）
LATEST_YEAR = int(os.getenv("LATEST_YEAR", "2026"))  # 令和8年


def year_label(year: int) -> str:
    """西暦 → 議会サイト上の年度ラベル（例: 2019 → 令和元年/平成31年）"""
    if year >= 2020:
        return f"令和{year - 2018}年"
    if year == 2019:
        return "令和元年/平成31年"
    if year == 1989:
        return "平成元年/昭和64年"
    return f"平成{year - 1988}年"


# (西暦, ラベル) 新しい順 / ラベルのみ古い順
TARGET_YEARS = [(y, year_label(y)) for y in range(LATEST_YEAR, START_YEAR - 1, -1)]
TARGET_YEAR_LABELS = [label for _, label in TARGET_YEARS]
YEAR_ORDER = list(reversed(TARGET_YEAR_LABELS))  # 古→新

# --- データベース ---
DB_PATH = os.getenv("DB_PATH", "data/gikai.db")

# --- スクレイピング設定 ---
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "2.0"))  # サーバー負荷軽減のため
HEADLESS = os.getenv("HEADLESS", "true").lower() == "true"

# --- Gemini AI ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

# 1リクエストあたりの最大文字数（コスト削減）
GEMINI_MAX_CHARS = int(os.getenv("GEMINI_MAX_CHARS", "3000"))
