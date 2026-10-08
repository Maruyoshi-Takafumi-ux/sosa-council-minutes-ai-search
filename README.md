# 匝瑳市議会 議事録AI検索くん

匝瑳市議会（千葉県）の公開会議録をキーワード全文検索し、Gemini で議員質問・市の答弁を要約する検索サービス。
川口市版（`kawaguchi-council-minutes-ai-search`）と同じ kaigiroku.net（SPS社）系システムのため、同一コードベースを流用。

- 会議録元: https://ssp.kaigiroku.net/tenant/sosa/SpTop.html （tenant=`sosa`, tenant_id=`212`）
- 公開予定: https://sosa.council-minutes-ai-search.jp （VPS上ポート 8002）
- 収録期間: 令和5年〜令和8年（4年分。公開は平成22年〜）。`START_YEAR`で変更可

## 匝瑳市の議事録の特徴
- 書式は松原市と同じ括弧書き（`○議長（都祭広一君）`）。
- 議員の質問のあと、**議長が答弁者を指名**してから課長等が答弁する（議員→議長→答弁者）。検索サイトの答弁取得は議長を飛ばして探すので問題ないが、課題抽出側（saitama-policy-db）は議長を飛ばす処理が必要。
- 市民病院（国保匝瑳市民病院）と農林水産の比重が大きい。

## 川口版からの変更点
| 項目 | 内容 |
|---|---|
| `src/config.py` | TENANT / TENANT_ID、年度リストを `START_YEAR`〜`LATEST_YEAR` から自動生成（`TARGET_YEARS`, `YEAR_ORDER`） |
| 年度リストの一元化 | `api.py` / `src/db.py` / `collect_all_years.py` は config を参照。**年度追加は `LATEST_YEAR` を上げるだけ** |
| `src/parser.py` | 匝瑳市は `◎奥ノ木信夫市長　本文` と**括弧なし**で役職・氏名が連結。役職語彙＋氏名長で分離（従来の括弧書式も対応） |
| `static/index.html` | 名称・JSON-LD・出典URL・年範囲 |
| `collect_all_years.py` | テナント名のハードコード廃止 |

## セットアップ
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
playwright install chromium          # VPSでは playwright install-deps chromium も
cp .env.example .env                 # GEMINI_API_KEY を設定

python collect_all_years.py          # 収集（数時間）。既存分はスキップされ再開可能
python summarize.py --parse          # 発言単位に解析（必須）
uvicorn api:app --host 0.0.0.0 --port 8002
```
全期間を取りたい場合: `START_YEAR=1995 python collect_all_years.py`（`LATEST_YEAR` も環境変数で上書き可）。

## 注意
- Playwright の既定UA（HeadlessChrome）だとサイト側が sorry ページへ転送し本文が空になる。`collect_all_years.py` は通常ブラウザUAを設定済み。独自スクリプトでも必ずUAを設定すること。
- 役職の語彙にない部署名は `src/parser.py` の `_DEPT_WORDS` に追加。
- 運営: 丸吉孝文 (@health-gear)
