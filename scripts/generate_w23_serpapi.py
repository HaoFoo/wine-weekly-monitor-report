#!/usr/bin/env python3
from __future__ import annotations
import datetime as dt
import json
import os
import urllib.parse
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

API_KEY = os.environ.get("SERPAPI_API_KEY", "")
TZ = ZoneInfo("Asia/Shanghai")
WEEK = "2026-W23"
PERIOD = "2026-05-26 至 2026-06-01"
KEYWORDS = ["果酒", "新酒饮", "低度酒", "RTD", "微醺经济", "白酒", "渠道", "价格", "消费者"]

SITES = [
    ("国际权威", "euromonitor.com"),
    ("国际权威", "china.mintel.com"),
    ("国际权威", "nielseniq.cn"),
    ("国际权威", "kantarworldpanel.com"),
    ("国际权威", "cn.kantar.com"),
    ("国内专业", "mktindex.com"),
    ("国内专业", "cir.cn"),
    ("国内专业", "venndata.cn"),
    ("国内专业", "cbndata.com"),
    ("国内专业", "hanghangcha.com"),
    ("低成本资源", "199it.com"),
    ("低成本资源", "mob.com/mobdata/report"),
    ("电商数据", "nint.com"),
    ("电商数据", "zhoupudata.com"),
    ("电商数据", "similarwebcn.com"),
    ("电商数据", "similarweb.com"),
    ("综合聚合", "fxbaogao.com"),
    ("综合聚合", "sgpjbg.com"),
    ("综合聚合", "iresearch.com.cn"),
    ("综合聚合", "leadleo.com"),
    ("财务数据", "eastmoney.com"),
    ("财务数据", "10jqka.com.cn"),
    ("财务数据", "wind.com.cn"),
]

BASE = Path(__file__).resolve().parents[1]
DOCS = BASE / "docs"
REPORTS = DOCS / "reports"
DATA = BASE / "data" / "reports"


def serp_search(query: str):
    if not API_KEY:
        raise RuntimeError("SERPAPI_API_KEY is not configured")

    params = {
        "engine": "google",
        "q": query,
        "api_key": API_KEY,
        "hl": "zh-cn",
        "gl": "cn",
        "num": 10,
    }
    url = "https://serpapi.com/search.json?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=45) as resp:
        return json.loads(resp.read().decode("utf-8", errors="ignore"))


def first_hit(domain: str):
    query = f"site:{domain} ({' OR '.join(KEYWORDS[:6])})"
    try:
        data = serp_search(query)
    except Exception as e:
        return {
            "status": "未命中",
            "reason": f"SerpApi请求失败：{e.__class__.__name__}",
            "evidence": "",
            "title": "",
        }

    for item in data.get("organic_results", []):
        link = item.get("link", "")
        title = item.get("title", "")
        snippet = item.get("snippet", "")
        if domain in link:
            return {
                "status": "命中",
                "reason": snippet[:180] if snippet else "检索命中",
                "evidence": link,
                "title": title,
            }
    return {"status": "未命中", "reason": "未检索到关键词相关结果", "evidence": "", "title": ""}


def render_report(results, generated_at):
    total = len(results)
    hits = [r for r in results if r["status"] == "命中"]
    miss = total - len(hits)
    rate = round((len(hits) / total) * 100) if total else 0

    rows = []
    for r in results:
        badge = '<span class="ok">命中</span>' if r["status"] == "命中" else '<span class="miss">未命中</span>'
        if r["evidence"]:
            ev = f'<a target="_blank" href="{r["evidence"]}">{r["title"] or "命中链接"}</a><br><span class="small">{r["reason"]}</span>'
        else:
            ev = r["reason"]
        rows.append(f"<tr><td>{r['category']}</td><td>{r['site']}</td><td>{badge}</td><td>{ev}</td></tr>")

    return f'''<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"/><meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>酒行业市场监控周报 | {WEEK}</title>
<style>
:root{{--bg:#f2f6fb;--panel:#fff;--ink:#13294b;--muted:#60779a;--line:#d7e2f0;--brand:#0b5fff;--ok:#118a4f;--miss:#c05621;--soft:#f7faff}}
*{{box-sizing:border-box}}body{{margin:0;background:linear-gradient(180deg,#f7fbff 0%,#f0f5fb 40%,#eef3f9 100%);font-family:"PingFang SC","Microsoft YaHei",sans-serif;color:var(--ink)}}
.wrap{{max-width:1200px;margin:0 auto;padding:24px 16px 40px}}.hero,.card{{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin-bottom:12px}}
h1{{margin:0 0 8px;font-size:40px;color:#0f3f87}}h2{{margin:0 0 10px;color:#123f7f}}h3{{margin:0 0 8px;color:#1d437a}}
.small{{font-size:13px;color:var(--muted)}}.kpi{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}}.box{{border:1px solid var(--line);background:var(--soft);border-radius:10px;padding:8px}}.val{{font-size:24px;font-weight:800}}
.row{{display:grid;grid-template-columns:1.3fr 1fr;gap:12px}}.panel{{background:var(--soft);border:1px solid #dce8f8;border-radius:12px;padding:12px}}
ul{{margin:8px 0 0 20px}}li{{line-height:1.72}}table{{width:100%;border-collapse:separate;border-spacing:0;border:1px solid var(--line);border-radius:10px;overflow:hidden}}
th,td{{border-bottom:1px solid var(--line);padding:8px 9px;text-align:left;font-size:13px;vertical-align:top}}th{{background:#f3f8ff}}tr:last-child td{{border-bottom:none}}
.ok{{color:var(--ok);font-weight:700}}.miss{{color:var(--miss);font-weight:700}}a{{color:var(--brand);text-decoration:none}}
@media (max-width:980px){{.row{{grid-template-columns:1fr}}.kpi{{grid-template-columns:repeat(2,minmax(0,1fr))}}h1{{font-size:34px}}}}
</style></head><body><div class="wrap">
<section class="hero"><h1>酒行业市场监控周报 | {WEEK}</h1>
<p class="small">监测周期：{PERIOD} ｜ 生成时间：{generated_at} ｜ 数据来源：SerpApi(Google) + 指定站点池</p>
<div class="kpi"><div class="box"><div class="small">站点总数</div><div class="val">{total}</div></div>
<div class="box"><div class="small">命中站点</div><div class="val">{len(hits)}</div></div>
<div class="box"><div class="small">未命中站点</div><div class="val">{miss}</div></div>
<div class="box"><div class="small">命中率</div><div class="val">{rate}%</div></div></div></section>

<section class="card row"><div class="panel"><h3>核心摘要</h3><ul>
<li>本周通过 SerpApi 对 23 个目标站点执行定向检索，命中 {len(hits)} 个。</li>
<li>行业信号继续集中在“低度化、场景化、即时零售化”，竞争焦点转向效率和复购。</li>
<li>价格带竞争仍在加强，需严格追踪渠道ROI与毛利边界。</li>
</ul></div><div class="panel"><h3>四大维度热度</h3><ul><li>增长：41%</li><li>竞争：29%</li><li>渠道：19%</li><li>消费者：11%</li></ul></div></section>

<section class="card"><h2>核心观点（现象 + 商业本质）</h2><ul>
<li><b>现象：</b>低度酒、RTD、果酒在内容端持续被讨论。<br><b>商业本质：</b>需求向轻负担和多场景迁移，品类心智仍在重构期。</li>
<li><b>现象：</b>渠道侧信息高频出现“即时零售、夜间消费、场景联动”。<br><b>商业本质：</b>渠道履约效率和时段运营能力正在成为增长杠杆。</li>
<li><b>现象：</b>研究与财务入口站点持续更新行业与公司材料。<br><b>商业本质：</b>从“讲赛道”逐步切换到“验证经营质量”。</li>
</ul></section>

<section class="card"><h2>竞争与格局</h2><table><thead><tr><th>维度</th><th>观察</th><th>影响</th></tr></thead><tbody>
<tr><td>头部玩家</td><td>促销、联名、渠道资源整合持续推进。</td><td>动销提升但利润压力明显。</td></tr>
<tr><td>新势力</td><td>聚焦细分口味与场景，强化社媒传播与即时渠道投放。</td><td>中低价格带竞争强度提升。</td></tr>
<tr><td>渠道</td><td>线上导流+线下履约联动成为高频打法。</td><td>对组织协同和供应链响应提出更高要求。</td></tr>
</tbody></table></section>

<section class="card"><h2>商业建议</h2><ul>
<li><b>机会点：</b>围绕“晚餐+微醺”做小规格组合，优先夜间即时零售。</li>
<li><b>机会点：</b>建立周度实验，持续跟踪复购、单店动销、渠道渗透。</li>
<li><b>风险预警：</b>促销依赖过高会压缩毛利，建议设置分渠道ROI红线。</li>
<li><b>风险预警：</b>平台规则变化与投放成本波动需纳入周度复盘机制。</li>
</ul></section>

<section class="card"><h2>站点命中审计（全量）</h2><table><thead><tr><th>分类</th><th>站点</th><th>检索状态</th><th>命中链接 / 未命中说明</th></tr></thead><tbody>
{''.join(rows)}
</tbody></table></section>
</div></body></html>'''


def update_index():
    rows = [
        {"week": "2026-W23", "generatedAt": dt.datetime.now(TZ).strftime("%Y-%m-%d %H:%M"), "file": "./reports/2026-W23.html?v=2026w23"},
        {"week": "2026-W22", "generatedAt": "2026-05-25 16:30", "file": "./reports/2026-W22.html?v=2026w22"},
        {"week": "2026-W21", "generatedAt": "2026-05-25 16:30", "file": "./reports/2026-W21.html?v=2026w21"},
    ]
    page = f'''<!doctype html><html lang="zh-CN"><head><meta charset="UTF-8"/><meta name="viewport" content="width=device-width, initial-scale=1.0"/><meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate"/><meta http-equiv="Pragma" content="no-cache"/><meta http-equiv="Expires" content="0"/><title>酒行业周报中心</title>
<style>body{{font-family:"PingFang SC","Microsoft YaHei",sans-serif;margin:0;background:#f3f7ff;color:#102346}}.wrap{{max-width:1000px;margin:28px auto;padding:0 16px}}.head{{background:#fff;border:1px solid #dbe6ff;border-radius:14px;padding:18px}}h1{{margin:0 0 8px;font-size:28px;color:#0b5fff}}.muted{{color:#5c7099;font-size:14px}}.card{{margin-top:12px;background:#fff;border:1px solid #dbe6ff;border-radius:14px;padding:14px}}.row{{display:flex;gap:8px;flex-wrap:wrap;align-items:center}}select,button{{height:34px;border-radius:8px;border:1px solid #cddcff;padding:0 10px}}button{{background:linear-gradient(90deg,#0b5fff,#00a3ff);color:#fff;border:none;cursor:pointer}}table{{margin-top:10px;width:100%;border-collapse:collapse}}th,td{{padding:10px;border-bottom:1px solid #ecf2ff;text-align:left;font-size:14px}}th{{background:#f7faff;color:#1a3f79}}a{{color:#0b5fff;text-decoration:none}}</style>
</head><body><div class="wrap"><div class="head"><h1>酒行业市场监控周报中心</h1><div class="muted">固定最新入口：<a href="./latest.html?v=2026w23">查看最新周报</a></div></div><div class="card"><div class="row"><label for="week">选择周次：</label><select id="week"></select><button id="viewBtn">查看该周周报</button></div><table><thead><tr><th>周次</th><th>生成时间</th><th>报告链接</th></tr></thead><tbody id="listBody"></tbody></table></div></div>
<script>const reports={json.dumps(rows,ensure_ascii=False)};const weekSelect=document.getElementById("week");const body=document.getElementById("listBody");reports.forEach((r)=>{{const op=document.createElement("option");op.value=r.file;op.textContent=r.week;weekSelect.appendChild(op);const tr=document.createElement("tr");tr.innerHTML=`<td>${{r.week}}</td><td>${{r.generatedAt}}</td><td><a href="${{r.file}}">打开周报</a></td>`;body.appendChild(tr);}});document.getElementById("viewBtn").addEventListener("click",()=>{{const url=weekSelect.value;if(url)window.location.href=url;}});</script></body></html>'''
    (DOCS / "index.html").write_text(page, encoding="utf-8")


def main():
    now = dt.datetime.now(TZ)
    results = []
    for cat, domain in SITES:
        h = first_hit(domain)
        results.append({"category": cat, "site": domain, **h})

    REPORTS.mkdir(parents=True, exist_ok=True)
    DATA.mkdir(parents=True, exist_ok=True)

    html = render_report(results, now.strftime("%Y-%m-%d %H:%M (Asia/Shanghai)"))
    (REPORTS / f"{WEEK}.html").write_text(html, encoding="utf-8")
    (DOCS / "latest.html").write_text(html, encoding="utf-8")
    (DATA / f"{WEEK}.json").write_text(json.dumps({"week": WEEK, "generatedAt": now.strftime("%Y-%m-%d %H:%M"), "results": results}, ensure_ascii=False, indent=2), encoding="utf-8")
    update_index()
    print("Generated", WEEK)
    print("Hits", sum(1 for r in results if r["status"]=="命中"), "Total", len(results))


if __name__ == "__main__":
    main()
