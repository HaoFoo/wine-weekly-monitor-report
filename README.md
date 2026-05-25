# 酒行业市场监控周报站点

## 已完成
- 周报中心页：`web/index.html`
- 最新周报固定链接：`web/latest.html`
- 历史周报页示例：`web/reports/2026-W21.html`
- 每周自动生成脚本骨架：`scripts/generate_weekly_report.sh`

## 使用
- 本地打开：`web/index.html`
- 生成新周报：`./scripts/generate_weekly_report.sh 2026-W22`

## 定时任务（示例）
每周一 08:30 自动运行（macOS crontab 示例）：

```cron
30 8 * * 1 /bin/bash /你的项目路径/scripts/generate_weekly_report.sh
```

后续接入真实采集逻辑后，即可每周自动更新 `web/latest.html`，打开固定链接即可看最新周报。
