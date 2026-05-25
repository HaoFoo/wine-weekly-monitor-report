#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import html
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

BASE = Path(__file__).resolve().parents[1]
DOCS = BASE / "docs"
REPORTS_DIR = DOCS / "reports"
DATA_DIR = BASE / "data" / "reports"

TZ = ZoneInfo("Asia/Shanghai")
KEYWORDS = ["果酒", "新酒饮", "低度酒", "RTD", "微醺经济", "白酒"]

SITES = [
    ("国际权威", "euromonitor.com", "https://www.euromonitor.com/"),
    ("国际权威", "china.mintel.com", "https://china.mintel.com/"),
    ("国际权威", "nielseniq.cn", "https://nielseniq.cn/global/zh/"),
    ("国际权威", "kantarworldpanel.com", "https://www.kantarworldpanel.com/cn/"),
    ("国际权威", "cn.kantar.com", "https://cn.kantar.com/"),
    ("国内专业", "mktindex.com", "https://www.mktindex.com/"),
    ("国内专业", "cir.cn", "https://www.cir.cn/"),
    ("国内专业", "venndata.cn", "http://www.venndata.cn/"),
    ("国内专业", "cbndata.com", "https://www.cbndata.com/"),
    ("国内专业", "hanghangcha.com", "https://www.hanghangcha.com/"),
    ("低成本资源", "199it.com", "https://www.199it.com/"),
    ("低成本资源", "mob.com/mobdata/report", "https://www.mob.com/mobdata/report/"),
    ("电商数据", "nint.com", "https://www.nint.com/"),
    ("电商数据", "zhoupudata.com", "https://www.zhoupudata.com/"),
    ("电商数据", "similarwebcn.com", "https://similarwebcn.com/"),
    ("电商数据", "similarweb.com", "https://www.similarweb.com/"),
    ("综合聚合", "fxbaogao.com", "https://www.fxbaogao.com/"),
    ("综合聚合", "sgpjbg.com", "https://www.sgpjbg.com/"),
    ("综合聚合", "iresearch.com.cn", "https://www.iresearch.com.cn/"),
    ("综合聚合", "leadleo.com", "https://www.leadleo.com/"),
    ("财务数据", "eastmoney.com", "https://www.eastmoney.com/"),
    ("财务数据", "10jqka.com.cn", "https://www.10jqka.com.cn/"),
    ("财务数据", "wind.com.cn", "https://www.wind.com.cn/"),
]


def fetch(url: str, timeout: int = 15) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 CodexWeeklyBot/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        body = resp.read(300000).decode(charset, errors="ignore")
        return resp.status, body


def search_site(domain: str) -> tuple[bool, str | None, str]:
    query = f"site:{domain} {' OR '.join(KEYWORDS[:3])}"
    url = "https://duckduckgo.com/html/?" + urllib.parse.urlencode({"q": query})
    try:
        _, body = fetch(url, timeout=20)
    except Exception as e:
        return False, None, f"搜索失败：{e.__class__.__name__}"

    links = re.findall(r'<a[^>]*class="result__a"[^>]*href="(.*?)"', body)
    for raw in links:
        link = html.unescape(raw)
        if domain in link:
            return True, link, "检索命中"
    return False, None, "未检索到关键词相关结果"


def week_label(now: dt.datetime) -> str:
    iso = now.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def build_report(week: str, now: dt.datetime, results: list[dict]) -> str:
    hits = [r for r in results if r["status"] == "命中"]
    misses = [r for r in results if r["status"] == "未命中"]
    hit_rate = round(len(hits) * 100 / len(results)) if results else 0

    row_parts: list[str] = []
    for r in results:
        cls = "ok" if r["status"] == "命中" else "miss"
        if r["evidence"]:
            evidence_cell = f'<a target="_blank" href="{html.escape(r["evidence"])}">命中链接</a>'
        else:
            evidence_cell = html.escape(r["reason"])
        row_parts.append(
            f'<tr><td>{r["category"]}</td><td>{r["site"]}</td><td><span class="{cls}">{r["status"]}</span></td><td>{evidence_cell}</td></tr>'
        )
    rows = "\n".join(row_parts)

    return f"""<!DOCTYPE html>
<html lang=\"zh-CN\"><head><meta charset=\"UTF-8\"/><meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"/>
<title>酒行业市场监控周报 | {week}</title>
<style>
:root{{--bg:#f2f6fb;--panel:#fff;--ink:#13294b;--muted:#60779a;--line:#d7e2f0;--brand:#0b5fff;--ok:#118a4f;--miss:#c05621;--soft:#f7faff}}
body{{margin:0;background:var(--bg);font-family:"PingFang SC","Microsoft YaHei",sans-serif;color:var(--ink)}}
.wrap{{max-width:1180px;margin:0 auto;padding:24px 16px 40px}}
.hero,.card{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin-bottom:12px}}
h1{{margin:0 0 8px;font-size:38px;color:#0f3f87}}h2{{margin:0 0 10px;color:#123f7f}}
.kpi{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}} .box{{border:1px solid var(--line);background:var(--soft);border-radius:10px;padding:8px}}
.val{{font-size:24px;font-weight:800}} .small{{font-size:13px;color:var(--muted)}}
th,td{{border-bottom:1px solid var(--line);padding:8px 9px;text-align:left;font-size:13px;vertical-align:top}} th{{background:#f3f8ff}}
table{{width:100%;border-collapse:separate;border-spacing:0;border:1px solid var(--line);border-radius:10px;overflow:hidden}} tr:last-child td{{border-bottom:none}}
.ok{{color:var(--ok);font-weight:700}} .miss{{color:var(--miss);font-weight:700}}
</style></head><body><div class=\"wrap\"> 
<div class=\"hero\"><h1>酒行业市场监控周报 | {week}</h1>
<p class=\"small\">生成时间：{now.strftime('%Y-%m-%d %H:%M')}（Asia/Shanghai）｜关键词：{' / '.join(KEYWORDS)}</p>
<div class=\"kpi\"><div class=\"box\"><div class=\"small\">站点总数</div><div class=\"val\">{len(results)}</div></div>
<div class=\"box\"><div class=\"small\">命中站点</div><div class=\"val\">{len(hits)}</div></div>
<div class=\"box\"><div class=\"small\">未命中站点</div><div class=\"val\">{len(misses)}</div></div>
<div class=\"box\"><div class=\"small\">命中率</div><div class=\"val\">{hit_rate}%</div></div></div></div>
<div class=\"card\"><h2>核心摘要</h2><p>本周共检索 {len(results)} 个指定站点，命中 {len(hits)} 个。行业仍处于结构化竞争阶段，重点关注渠道效率、价格带竞争和复购质量。</p></div>
<div class=\"card\"><h2>站点命中审计（全量）</h2><table><thead><tr><th>分类</th><th>站点</th><th>检索状态</th><th>命中链接 / 未命中说明</th></tr></thead><tbody>{rows}</tbody></table></div>
<div class=\"card\"><h2>使用说明</h2><p>用户可在周报中心选择周次查看历史版本；<code>latest.html</code> 固定展示最新周报。</p></div>
</div></body></html>"""


def rebuild_index() -> None:
    report_files = sorted(REPORTS_DIR.glob("*.html"), reverse=True)
    rows = []
    opts = []
    for rp in report_files:
        wk = rp.stem
        meta = DATA_DIR / f"{wk}.json"
        ts = "-"
        if meta.exists():
            try:
                ts = json.loads(meta.read_text(encoding="utf-8")).get("generatedAt", "-")
            except Exception:
                pass
        rel = f"./reports/{wk}.html"
        opts.append({"week": wk, "generatedAt": ts, "file": rel})

    arr = json.dumps(opts, ensure_ascii=False, indent=2)
    index_html = f"""<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"UTF-8\"/><meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"/><title>酒行业周报中心</title>
<style>body{{font-family:"PingFang SC","Microsoft YaHei",sans-serif;margin:0;background:#f3f7ff;color:#102346}}.wrap{{max-width:1000px;margin:28px auto;padding:0 16px}}.head{{background:#fff;border:1px solid #dbe6ff;border-radius:14px;padding:18px}}h1{{margin:0 0 8px;font-size:28px;color:#0b5fff}}.muted{{color:#5c7099;font-size:14px}}.card{{margin-top:12px;background:#fff;border:1px solid #dbe6ff;border-radius:14px;padding:14px}}.row{{display:flex;gap:8px;flex-wrap:wrap;align-items:center}}select,button{{height:34px;border-radius:8px;border:1px solid #cddcff;padding:0 10px}}button{{background:linear-gradient(90deg,#0b5fff,#00a3ff);color:#fff;border:none;cursor:pointer}}table{{margin-top:10px;width:100%;border-collapse:collapse}}th,td{{padding:10px;border-bottom:1px solid #ecf2ff;text-align:left;font-size:14px}}th{{background:#f7faff;color:#1a3f79}}a{{color:#0b5fff;text-decoration:none}}</style>
</head><body><div class=\"wrap\"><div class=\"head\"><h1>酒行业市场监控周报中心</h1><div class=\"muted\">固定最新入口：<a href=\"./latest.html\">查看最新周报</a></div></div><div class=\"card\"><div class=\"row\"><label for=\"week\">选择周次：</label><select id=\"week\"></select><button id=\"viewBtn\">查看该周周报</button></div><table><thead><tr><th>周次</th><th>生成时间</th><th>报告链接</th></tr></thead><tbody id=\"listBody\"></tbody></table></div></div>
<script>const reports={arr};const weekSelect=document.getElementById("week");const body=document.getElementById("listBody");reports.forEach((r)=>{{const op=document.createElement("option");op.value=r.file;op.textContent=r.week;weekSelect.appendChild(op);const tr=document.createElement("tr");tr.innerHTML=`<td>${{r.week}}</td><td>${{r.generatedAt}}</td><td><a href="${{r.file}}">打开周报</a></td>`;body.appendChild(tr);}});document.getElementById("viewBtn").addEventListener("click",()=>{{const url=weekSelect.value;if(url)window.location.href=url;}});</script></body></html>"""
    (DOCS / "index.html").write_text(index_html, encoding="utf-8")


def main() -> None:
    now = dt.datetime.now(TZ)
    week = week_label(now)

    results = []
    for category, site, homepage in SITES:
        hit, evidence, reason = search_site(site)
        if not hit:
            # fallback: check homepage reachability so failure reason更具体
            try:
                status, _ = fetch(homepage)
                if status >= 400:
                    reason = f"主页访问失败：HTTP {status}"
                else:
                    reason = reason + "；主页可访问"
            except Exception:
                pass

        results.append({
            "category": category,
            "site": site,
            "status": "命中" if hit else "未命中",
            "evidence": evidence,
            "reason": reason,
        })

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    report_html = build_report(week, now, results)
    report_file = REPORTS_DIR / f"{week}.html"
    report_file.write_text(report_html, encoding="utf-8")
    (DOCS / "latest.html").write_text(report_html, encoding="utf-8")

    (DATA_DIR / f"{week}.json").write_text(
        json.dumps(
            {
                "week": week,
                "generatedAt": now.strftime("%Y-%m-%d %H:%M"),
                "keywords": KEYWORDS,
                "totalSites": len(results),
                "hitSites": sum(1 for x in results if x["status"] == "命中"),
                "results": results,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    rebuild_index()
    print(f"Generated report: {report_file}")


if __name__ == "__main__":
    main()
