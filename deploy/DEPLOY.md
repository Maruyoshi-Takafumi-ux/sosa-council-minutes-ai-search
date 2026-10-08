# 匝瑳市版 VPSデプロイ手順（松原市・川口市と同一VPSに同居）

松原市は port 8000 / `gijiroku`、川口市は port 8001 / `gijiroku-kawaguchi` で稼働中のため、匝瑳市は **port 8002 / `gijiroku-sosa`** を使う。

0. **事前確認**: `bash deploy/vps_check.sh`（読み取りのみ）→ 出力を共有
1. **DNS**（ムームードメイン）: ホスト名 `sosa` / A / 160.251.174.200（松原・川口と同じVPS）
2. **配置**
   ```bash
   git clone https://github.com/Maruyoshi-Takafumi-ux/sosa-council-minutes-ai-search.git /opt/sosa-council-minutes-ai-search
   cd /opt/sosa-council-minutes-ai-search
   python3 -m venv venv && source venv/bin/activate
   pip install -r requirements.txt && mkdir -p data
   cp /opt/kawaguchi-council-minutes-ai-search/.env .env && chmod 600 .env   # 川口市と同じキー・モデル（gemini-3.5-flash）。キーはチャットに貼らない
   ```
3. **DB**: ローカルで検証済みの `data/gikai.db` を `scp` で転送するか、VPSで `python collect_all_years.py && python summarize.py --parse`
4. **サービス**
   ```bash
   cp deploy/gijiroku-sosa.service /etc/systemd/system/
   systemctl daemon-reload && systemctl enable --now gijiroku-sosa
   curl -s http://127.0.0.1:8002/api/years
   ```
5. **Nginx / SSL**（DNS反映後）
   ```bash
   cp deploy/nginx-sosa.conf /etc/nginx/sites-available/sosa
   ln -s /etc/nginx/sites-available/sosa /etc/nginx/sites-enabled/
   nginx -t && systemctl reload nginx
   certbot --nginx -d sosa.council-minutes-ai-search.jp
   ```
   ※ `reload` を使う（`restart` だと松原市が一瞬止まる）。
6. **LLMO**: Search Console にプロパティ追加 → `google-site-verification` を `<title>` 直後に挿入 → 再起動
