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


# 会議録（出典）リンクを表示する発言者。カンマ区切りで複数指定可。空にすると全員に表示する。
SOURCE_LINK_SPEAKERS = [n.strip() for n in os.getenv("SOURCE_LINK_SPEAKERS", "近藤魁人").split(",") if n.strip()]


def minute_source_url(council_id: int, schedule_id: int, minute_no: int | None,
                      speaker_name: str = "") -> str | None:
    """会議録検索システムで、その発言の位置に直接飛ぶURL。
    minute_no が無い、または SOURCE_LINK_SPEAKERS に含まれない発言者のときは None。
    minute_id は、会議録ページに並ぶブロック（見出し・議長・議員・答弁者の発言）の上からの通し番号。"""
    if not minute_no:
        return None
    if SOURCE_LINK_SPEAKERS and speaker_name not in SOURCE_LINK_SPEAKERS:
        return None
    return (f"{MINUTE_VIEW_URL}?council_id={council_id}&schedule_id={schedule_id}"
            f"&minute_id={minute_no}&is_search=true")


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
