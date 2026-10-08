"""Standalone, escaped HTML execution reports with embedded screenshot evidence."""

import base64
import html
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path


def esc(value):
    return html.escape(str(value), quote=True)


def local_time(value):
    return datetime.fromisoformat(value).astimezone(timezone(timedelta(hours=7))).strftime("%d/%m/%Y %H:%M:%S UTC+7")


def write_html_report(data, destination):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    counts = {status: data["counts"].get(status, 0) for status in ("PASS", "FAIL", "SKIPPED", "BLOCKED")}
    ids = {row["id"] for row in data["results"]}
    actual = counts["PASS"] + counts["FAIL"]
    cards = "".join(f'<div class="stat {status.lower()}"><span>{status}</span><strong>{count}</strong></div>' for status, count in counts.items())
    rows = []
    for row in sorted(data["results"], key=lambda item: (item["id"], item["test"])):
        observation = row.get("observed", {})
        message = observation.get("error_text") or row.get("reason") or "Không ghi nhận thông báo."
        details = []
        if row.get("input"):
            details.append('<h4>Dữ liệu đã nhập</h4><pre>' + esc(json.dumps(row["input"], ensure_ascii=False, indent=2)) + '</pre>')
        if observation:
            details.append('<h4>Quan sát sau submit</h4><pre>' + esc(json.dumps(observation, ensure_ascii=False, indent=2)) + '</pre>')
        if row.get("reason"):
            details.append('<h4>Chi tiết kết quả</h4><pre>' + esc(row["reason"]) + '</pre>')
        for filename in row.get("evidence", []):
            image = Path(filename)
            if image.is_file():
                encoded = base64.b64encode(image.read_bytes()).decode("ascii")
                details.append(f'<figure><img alt="Ảnh bằng chứng {esc(row["id"])}" loading="lazy" src="data:image/png;base64,{encoded}"><figcaption>{esc(image.name)}</figcaption></figure>')
        name = row["test"].split("::")[-1]
        browser = " ".join(filter(None, (row.get("browser"), row.get("browser_version")))) or "Chưa mở trình duyệt"
        status = row["status"]
        rows.append(f'''<tr data-status="{status}"><td><b>{esc(row['id'])}</b><small>{esc(name)}</small></td>
<td><span class="badge {status.lower()}">{status}</span><small>{esc(row['phase'])}</small></td>
<td>{row['duration_seconds']:.2f} s<small>{esc(browser)}</small></td>
<td><div class="message">{esc(message)}</div><details><summary>Xem chi tiết và bằng chứng</summary>{''.join(details)}</details></td></tr>''')
    mode = "FORM THAM CHIẾU CỤC BỘ" if data["demo"] else "CHẠY TRỰC TIẾP TRÊN HỆ THỐNG ĐÍCH"
    summary = f"{len(ids)} ID · {len(data['results'])} lượt · {actual} lượt đã thực thi · {counts['SKIPPED'] + counts['BLOCKED']} lượt chưa thực thi"
    page = '''<!doctype html><html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Báo cáo Selenium — đăng nhập UTC</title><style>
:root{font-family:Segoe UI,Arial,sans-serif;color:#172b3a;background:#f4f6f8;line-height:1.5}*{box-sizing:border-box}body{margin:0}main{max-width:1420px;margin:auto;padding:40px 32px}header{border-top:5px solid #245c77;padding-top:24px}h1{font-size:32px;line-height:1.2;margin:8px 0 14px}h2{font-size:19px;margin:0}h4{margin-bottom:7px}.eyebrow{font-size:12px;font-weight:700;letter-spacing:1.4px;color:#3c6378}.meta{display:flex;flex-wrap:wrap;gap:10px 28px;color:#536573;font-size:14px}a{color:#245c77}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:26px 0}.stat{background:white;border:1px solid #dce3e7;border-top:4px solid #9aa9b3;padding:16px 22px}.stat span{display:block;font-weight:600;font-size:12px;letter-spacing:1px}.stat strong{font-size:34px}.stat.pass{border-top-color:#26744b}.stat.fail{border-top-color:#b53a3a}.stat.skipped{border-top-color:#b28323}.stat.blocked{border-top-color:#637486}.notice{background:#edf2f6;border-left:4px solid #6b8193;padding:14px 18px;font-size:14px;margin:20px 0 24px}.toolbar{display:flex;justify-content:space-between;align-items:center;gap:16px;flex-wrap:wrap;margin-bottom:14px}.filters{display:flex;gap:8px;flex-wrap:wrap}input,select,button{font:inherit;padding:9px 12px;border:1px solid #c9d4db;background:white;border-radius:3px}input{min-width:270px}button{cursor:pointer}table{width:100%;border-collapse:collapse;background:#fff;table-layout:fixed}th{text-align:left;background:#e9eef2;font-size:12px;text-transform:uppercase;letter-spacing:.5px}th,td{padding:15px 18px;border-bottom:1px solid #dce3e7;vertical-align:top}th:nth-child(1){width:25%}th:nth-child(2){width:12%}th:nth-child(3){width:16%}th:nth-child(4){width:47%}td small{display:block;color:#627581;font-size:12px;overflow-wrap:anywhere;margin-top:7px}.badge{display:inline-block;padding:3px 9px;font-size:11px;font-weight:700;border-radius:3px}.badge.pass{background:#e1f1e6;color:#21623e}.badge.fail{background:#fbe5e5;color:#9e3030}.badge.skipped{background:#fff1d6;color:#866115}.badge.blocked{background:#e7edf2;color:#4e6273}.message{white-space:pre-wrap;overflow-wrap:anywhere;max-height:110px;overflow:auto;font-size:14px}details{margin-top:12px}summary{cursor:pointer;color:#245c77;font-size:13px}pre{background:#f4f6f8;padding:12px;white-space:pre-wrap;overflow-wrap:anywhere;font-size:12px;border:1px solid #e1e7eb}figure{margin:18px 0 0}img{display:block;width:100%;height:auto;border:1px solid #d9e1e6}figcaption,footer{font-size:12px;color:#637581}footer{margin-top:24px}.empty{display:none;padding:25px;text-align:center}tr[hidden]{display:none}@media(max-width:800px){main{padding:24px 12px}.stats{gap:8px}.stat{padding:10px}table{table-layout:auto;min-width:850px}.table-wrap{overflow:auto}}@media print{.toolbar{display:none}body{background:white}main{padding:10px}.stats{break-inside:avoid}details>*{display:block}.message{max-height:none}tr{break-inside:avoid}figure{break-inside:avoid}}
</style></head><body><main><header><div class="eyebrow">__MODE__ · SELENIUM / PYTEST</div><h1>Báo cáo kiểm thử đăng nhập UTC</h1><div class="meta"><span>Đích: <a href="__TARGET__">__TARGET__</a></span><span>Bắt đầu: __START__</span><span>Kết thúc: __END__</span></div><p>__SUMMARY__</p></header><section class="stats">__CARDS__</section>
<div class="notice"><b>Cách đọc kết quả:</b> PASS nghĩa là ứng dụng từ chối đăng nhập đúng mong đợi của negative testcase. SKIPPED/BLOCKED là các lượt chưa thực thi, không được tính là PASS. Ca CAPTCHA cần challenge thực tế; ca thiếu dữ liệu hoặc đặc tả được ghi rõ lý do.</div>
__NOTES__<div class="toolbar"><h2>Chi tiết từng lượt <span id="visible-count"></span></h2><div class="filters"><input id="search" type="search" aria-label="Tìm testcase" placeholder="Tìm ID, tên hoặc thông báo"><select id="status" aria-label="Lọc trạng thái"><option value="all">Tất cả trạng thái</option><option>PASS</option><option>FAIL</option><option>SKIPPED</option><option>BLOCKED</option></select><button id="print" type="button">In / lưu PDF</button></div></div>
<div class="table-wrap"><table><thead><tr><th>Testcase / biến thể</th><th>Kết quả</th><th>Thời gian / trình duyệt</th><th>Thông báo thực tế và bằng chứng</th></tr></thead><tbody>__ROWS__</tbody></table><div class="empty" id="empty">Không có kết quả phù hợp.</div></div><footer>Run ID: __RUN__ · Môi trường: __ENV__ · Pytest exit code: __EXIT__ · HTML độc lập; ảnh bằng chứng đã nhúng trong file, không cần mạng để đọc báo cáo.</footer></main>
<script>(()=>{const rows=[...document.querySelectorAll('tbody tr')],search=document.getElementById('search'),status=document.getElementById('status');function filter(){let visible=0;for(const row of rows){row.hidden=!((status.value==='all'||row.dataset.status===status.value)&&row.textContent.toLocaleLowerCase('vi').includes(search.value.toLocaleLowerCase('vi')));if(!row.hidden)visible++;}document.getElementById('visible-count').textContent='('+visible+'/'+rows.length+')';document.getElementById('empty').style.display=visible?'none':'block';}search.addEventListener('input',filter);status.addEventListener('change',filter);document.getElementById('print').addEventListener('click',()=>window.print());filter();})();</script></body></html>'''
    notes = "".join('<div class="notice">' + esc(note) + '</div>' for note in data.get("notes", []))
    replacements = {"MODE": esc(mode), "TARGET": esc(data["target"]), "START": esc(local_time(data["started_utc"])), "END": esc(local_time(data["finished_utc"])), "SUMMARY": esc(summary), "CARDS": cards, "ROWS": "".join(rows), "NOTES": notes, "RUN": esc(data["run_id"]), "ENV": esc(data["environment"]), "EXIT": str(data["exit_code"])}
    for key, value in replacements.items():
        page = page.replace("__" + key + "__", value)
    destination.write_text(page, encoding="utf-8")
