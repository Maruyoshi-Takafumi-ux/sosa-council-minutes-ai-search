# 匝瑳市議会 議事録AI検索くん — 引き継ぎメモ
川口市版（~/Desktop/埼玉県内議事録/kawaguchi-council-minutes-ai-search）をもとにした匝瑳市版。顧客（匝瑳市の議員）向けの案件。
- tenant=sosa, tenant_id=212 / 収録は src/config.py の START_YEAR(2023), LATEST_YEAR(2026)
- 本番: 松原・川口と同一VPS。port 8002 / gijiroku-sosa / /opt/sosa-council-minutes-ai-search / sosa.council-minutes-ai-search.jp。Nginxは reload（restartしない）
- 課題抽出・レポートは ~/Desktop/埼玉県内議事録/saitama-policy-db（municipalities.py の "sosa"）。顧客データは別DB: POLICY_DB=~/Desktop/匝瑳市議事録/policy_sosa.db
- AI要約は gemini-3.5-flash + 思考最小（src/summarizer.py の GEN_CONFIG）
- 収集・抽出はMacで行い、DB(data/gikai.db)をscpで転送（VPSはメモリ不足）。Gemini APIは実行前に見積もり+許可
