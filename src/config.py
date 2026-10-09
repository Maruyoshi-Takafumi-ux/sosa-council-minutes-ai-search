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


# 議会中継（録画）。匝瑳市議会の公式の中継サービスへのリンク（動画の複製はしない）。
# 会議録の (council_id, schedule_id) → 中継サービスの (council_id, schedule_id, playlist_id, 年)。
# 一般質問の日（本会議）だけ。SOURCE_LINK_SPEAKERS の発言者にのみ表示する（speaker_id=24 は近藤魁人）。
VIDEO_BASE_URL = "https://smart.discussvision.net/smart/tenant/sosa/WebView/rd/speech.html"
VIDEO_SPEAKER_ID = 24
VIDEO_BY_MINUTES = {
    (117, 5): (69, 6, 1, 2023), (118, 5): (70, 5, 4, 2023), (121, 5): (71, 5, 2, 2023), (123, 5): (73, 5, 3, 2023),
    (125, 5): (74, 6, 2, 2024), (127, 5): (75, 5, 3, 2024), (129, 5): (76, 6, 2, 2024), (131, 5): (78, 5, 4, 2024),
    (133, 5): (79, 6, 3, 2025), (135, 4): (80, 4, 5, 2025), (137, 4): (81, 5, 5, 2025), (139, 5): (83, 5, 4, 2025),
    (141, 4): (84, 5, 4, 2026), (143, 4): (85, 4, 4, 2026),
}


def video_url(council_id: int, schedule_id: int, speaker_name: str = "") -> str | None:
    """議会中継の録画ページのURL。対象外の発言者・日付のときは None。"""
    if SOURCE_LINK_SPEAKERS and speaker_name not in SOURCE_LINK_SPEAKERS:
        return None
    v = VIDEO_BY_MINUTES.get((council_id, schedule_id))
    if not v:
        return None
    c, s, p, y = v
    return (f"{VIDEO_BASE_URL}?council_id={c}&schedule_id={s}&playlist_id={p}"
            f"&speaker_id={VIDEO_SPEAKER_ID}&target_year={y}&tab_id=1")


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
