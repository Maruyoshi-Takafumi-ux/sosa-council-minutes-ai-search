"""
議事録テキストの解析モジュール

テキスト形式（松原市: 括弧書式 / 川口市: 括弧なし連結書式の両方に対応）：
  川口市: ○古川九一議長　本文 / ◆２７番（若谷正巳議員）　本文 / ◎奥ノ木信夫市長　本文
  P.5 議長（河内徹君）
  ○議長（河内徹君） おはようございます...
  ～～～～ (区切り線)
  P.9 11番（河本晋一君）
  ◆11番（河本晋一君） 質問内容...
  P.9 総務部長（鶴山隆二君）
  ◎総務部長（鶴山隆二君） 答弁内容...

発言者タイプ：
  ○ = 議長 (chair)
  ◆ = 議員・委員 (member) ← 質問する側
  ◎ = 市長・副市長・部長等 (official) ← 答弁する側
"""

import re
from typing import Optional


# 発言開始のパターン
SPEECH_PATTERN = re.compile(
    r'^([○◆◎])\s*(.+?)\s*[（(](.+?)[）)]\s+(.*)',
    re.DOTALL
)

# ページ番号のパターン（例: "P.5"）
PAGE_PATTERN = re.compile(r'^P\.(\d+)')

# 区切り線パターン
SEPARATOR_PATTERN = re.compile(r'^～{5,}')

# 発言タイプのマッピング
TYPE_MAP = {
    "○": "chair",     # 議長
    "◆": "member",    # 議員
    "◎": "official",  # 市側
}


def _clean_name(raw: str) -> tuple[str, str]:
    """
    発言者名と役職を分離する
    例: '11番（河本晋一君）' → name='河本晋一', role='11番議員'
    例: '総務部長（鶴山隆二君）' → name='鶴山隆二', role='総務部長'
    例: '議長（河内徹君）' → name='河内徹', role='議長'
    """
    # 番号付き議員: "11番（河本晋一君）" のような形式が入力されることも
    # ここでは speaker_marker 部分のみ入力される
    # role=raw の中の（）の外、name=（）の中
    m = re.match(r'^(.+?)[（(](.+?)[）)]', raw.strip())
    if m:
        role = m.group(1).strip()
        name = re.sub(r'(議員|委員|君)$', '', m.group(2).strip())
        return name, role
    return raw.strip(), ""


# --- 括弧なし書式（川口市）: 「奥ノ木信夫市長」→ 氏名 + 役職 に分離する ---
_DEPT_WORDS = (
    "市長室|企画財政|企画|財政|理財|総務|危機管理|市民生活|市民|福祉|子ども|こども|保健|健康|環境|経済|産業|"
    "建設|都市計画|都市整備|都市|土木|道路|上下水道局|上下水道|水道|医療センター|病院|教育総務|学校教育|"
    "生涯学習|文化|スポーツ|消防|選管|選挙管理委員会|監査|会計|議会|政策審議|行政|契約|資産|税務|"
    "技監|総合|事業|管理|事務|施設|地域|公園|下水道|農業|商工|観光|人事|秘書|広報|情報|防災|"
    "高齢|障害|介護|生活|青少年|学務|指導|教育"
)
_TITLE_RE = re.compile(
    r"^(?:副?市長|市長室長|副?教育長|消防長|副?議長|副?委員長|代表監査委員|監査委員|会計管理者|"
    r"(?:上下水道)?事業管理者|企業管理者|病院事業管理者|技監|"
    rf"(?:{_DEPT_WORDS})*(?:事務局長|部長|局長|次長|課長|室長|所長|館長|参事|理事|主幹))$"
)
# 語彙にない部署名のためのフォールバック
_TITLE_GENERIC_RE = re.compile(r"^\S{1,10}(?:部長|局長|次長|課長|室長|所長|館長|事務局長|参事|理事|管理者|監査委員)$")


def _split_name_title(head: str) -> tuple[str, str]:
    """'奥ノ木信夫市長' → ('奥ノ木信夫', '市長')。氏名は4→3→5→2→6文字の順で試す"""
    head = head.strip()
    if head.endswith("議員"):
        return head[:-2], "議員"
    for regex in (_TITLE_RE, _TITLE_GENERIC_RE):
        for k in (4, 3, 5, 2, 6):
            if len(head) > k and regex.match(head[k:]):
                return head[:k], head[k:]
    return head, ""


def parse_transcript(raw_text: str) -> list[dict]:
    """
    議事録の生テキストを発言リストに変換する

    Returns:
        list of dict with keys:
            order_num, page_num, speaker_name, speaker_role,
            speaker_type, content
    """
    speeches = []
    current_page = None
    current_type = None
    current_raw_speaker = None
    current_lines = []
    order = 0

    def flush():
        nonlocal order
        if current_type and current_raw_speaker and current_lines:
            content = "\n".join(current_lines).strip()
            # 最初の行に発言者名が含まれていることがあるので除去
            if content:
                name, role = _clean_name(current_raw_speaker)
                speeches.append({
                    "order_num": order,
                    "page_num": current_page,
                    "speaker_name": name,
                    "speaker_role": role,
                    "speaker_type": TYPE_MAP.get(current_type, "other"),
                    "content": content,
                })
                order += 1

    lines = raw_text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # 区切り線はスキップ
        if SEPARATOR_PATTERN.match(line) or line == "以上" or not line:
            i += 1
            continue

        # ページ番号行（"P.5 議長（河内徹君）" のパターン）
        page_match = PAGE_PATTERN.match(line)
        if page_match:
            current_page = int(page_match.group(1))
            i += 1
            continue

        # 発言開始行（○、◆、◎ で始まる）
        if line and line[0] in ("○", "◆", "◎"):
            marker = line[0]
            rest = line[1:].strip()

            # 括弧書式: 「議長（河内徹君） 本文」「２７番（若谷正巳議員）　本文」
            m_paren = re.match(r'^(\S+?[）)])\s*(.*)', rest, re.DOTALL)
            if m_paren:
                raw_speaker, body = m_paren.group(1), m_paren.group(2)
            else:
                # 括弧なし書式（川口市）: 「奥ノ木信夫市長　本文」
                m_plain = re.match(r'^(\S+)(?:\s+(.*))?$', rest, re.DOTALL)
                if not m_plain:
                    raw_speaker, body = None, ""
                else:
                    name, role = _split_name_title(m_plain.group(1))
                    raw_speaker, body = f"{role}（{name}）", m_plain.group(2) or ""
            if raw_speaker:
                flush()
                current_type = marker
                current_raw_speaker = raw_speaker.strip()
                current_lines = []
                body = body.strip()
                if body:
                    current_lines.append(body)
                i += 1
                continue

        # 継続行（現在の発言の続き）
        if current_type and line:
            current_lines.append(line)

        i += 1

    flush()
    return speeches


def compute_minute_nos(raw_text: str) -> list[int]:
    """○◆◎ の発言ごとに、会議録検索システム上のブロック番号（minute_id）を、出現順に返す。

    会議録ページは「先頭の見出しブロック」＋「△○◆◎で始まる各ブロック」が1行ずつ並ぶ。
    minute_id は、その行を上から数えた番号（1始まり）。先頭ブロックが1、k番目（0始まり）のマーカー行は k+2。
    """
    nos = []
    k = 0
    for line in raw_text.splitlines():
        if line and line[0] in "△○◆◎":
            if line[0] in "○◆◎":
                nos.append(k + 2)
            k += 1
    return nos


def pair_qa(speeches: list[dict]) -> list[tuple[dict, Optional[dict]]]:
    """
    議員の質問と直後の市側答弁をペアリングする

    Returns:
        list of (question_speech, answer_speech_or_None)
    """
    pairs = []
    i = 0
    while i < len(speeches):
        sp = speeches[i]
        if sp["speaker_type"] == "member":
            # 直後の official 発言を答弁として取得
            answer = None
            if i + 1 < len(speeches) and speeches[i + 1]["speaker_type"] == "official":
                answer = speeches[i + 1]
                i += 2
            else:
                i += 1
            pairs.append((sp, answer))
        else:
            i += 1
    return pairs
