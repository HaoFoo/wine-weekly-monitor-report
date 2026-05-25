#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
WEB_DIR="$ROOT_DIR/web"
REPORTS_DIR="$WEB_DIR/reports"
DATA_DIR="$ROOT_DIR/data/reports"

WEEK="${1:-$(date +%G-W%V)}"
NOW="$(date '+%Y-%m-%d %H:%M')"
REPORT_FILE="$REPORTS_DIR/$WEEK.html"
DATA_FILE="$DATA_DIR/$WEEK.json"

mkdir -p "$REPORTS_DIR" "$DATA_DIR"

cat > "$REPORT_FILE" <<HTML
<!doctype html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"><title>酒行业市场监控周报 $WEEK</title></head><body style="font-family:PingFang SC,Microsoft YaHei,sans-serif;max-width:900px;margin:24px auto;padding:0 16px"><h1>酒行业市场监控周报｜$WEEK</h1><p>生成时间：$NOW</p><p>这是自动任务生成的周报页面。下一步请接入真实抓取与AI摘要逻辑。</p><p><a href="../index.html">返回周报中心</a></p></body></html>
HTML

cat > "$DATA_FILE" <<JSON
{"week":"$WEEK","generatedAt":"$NOW","status":"generated"}
JSON

cp "$REPORT_FILE" "$WEB_DIR/latest.html"
echo "Generated: $REPORT_FILE"
