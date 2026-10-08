"""Combine live runs, retaining the newest result and its provenance per variant."""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/test/python"))

from e2e.base.html_report import write_html_report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reports", nargs="+", type=Path)
    parser.add_argument("--html", required=True, type=Path)
    args = parser.parse_args()
    sources = sorted((json.loads(path.read_text(encoding="utf-8")) for path in args.reports), key=lambda source: source["finished_utc"])
    if len({(source["target"], source["environment"], source["demo"]) for source in sources}) != 1:
        parser.error("Reports must use the same target, environment and reference/live mode")
    latest = {}
    for source in sources:
        for result in source["results"]:
            latest[result["test"]] = dict(result, source_run_id=source["run_id"], source_started_utc=source["started_utc"], source_finished_utc=source["finished_utc"])
    results = sorted(latest.values(), key=lambda row: row["test"])
    data = {
        "run_id": "aggregate-" + sources[-1]["run_id"], "report_kind": "aggregate",
        "started_utc": sources[0]["started_utc"], "finished_utc": sources[-1]["finished_utc"],
        "target": sources[0]["target"], "environment": sources[0]["environment"], "demo": sources[0]["demo"],
        "exit_code": "N/A (tổng hợp nhiều lượt chạy)", "collected": len(results),
        "counts": dict(Counter(row["status"] for row in results)), "results": results,
        "source_runs": [{key: source[key] for key in ("run_id", "started_utc", "finished_utc", "counts", "exit_code")} for source in sources],
        "notes": ["Báo cáo tổng hợp nhiều đợt chạy trên cùng hệ thống, không phải một lượt pytest duy nhất. Mỗi biến thể dùng kết quả mới nhất trong các nguồn đã chọn; thời điểm và Run ID nguồn nằm trong chi tiết. Không chạy lại testcase khi tổng hợp."],
    }
    args.html.parent.mkdir(parents=True, exist_ok=True)
    args.html.with_suffix(".json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    write_html_report(data, args.html)
    print(json.dumps(data["counts"]))


if __name__ == "__main__":
    main()
