#!/bin/bash
# VPS の現状確認（読み取りのみ。何も変更しない）。VPS上で実行し、出力を共有する。
echo "== OS / Python =="; lsb_release -d 2>/dev/null; python3 --version
echo "== ディスク / メモリ =="; df -h / | tail -1; free -h | sed -n 2p
echo "== 稼働中の議事録サービス =="; systemctl list-units 'gijiroku*' --no-pager 2>/dev/null
echo "== 使用中ポート(8000-8010) =="; ss -ltnp 2>/dev/null | grep -E ':80[0-9][0-9]\b'
echo "== /opt =="; ls /opt
echo "== Nginx サイト =="; ls /etc/nginx/sites-enabled/; nginx -t 2>&1 | tail -2
echo "== 既存SSL証明書 =="; certbot certificates 2>/dev/null | grep -E "Certificate Name|Domains|Expiry"
echo "== Playwright/Chromium =="; ls ~/.cache/ms-playwright 2>/dev/null
echo "== DNS (sosa サブドメイン) =="; getent hosts sosa.council-minutes-ai-search.jp || echo "未解決（ムームードメインでAレコード未設定/未反映）"
echo "== このVPSのIP =="; curl -s -m 5 ifconfig.me; echo
