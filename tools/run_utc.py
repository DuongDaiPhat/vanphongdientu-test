"""Run the suite against UTC using observed oracles and write a standalone HTML report."""

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/test/python"))

import pytest

from e2e.base.settings import load_env


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--include-payloads", action="store_true", help="Also run the one-submit SQL/XSS and 256-character username cases directly on UTC")
    parser.add_argument("--html", default="reports/utc-live/report.html", help="Standalone report output")
    args = parser.parse_args()
    load_env(ROOT / "config/utc.env")
    if os.environ.get("BASE_URL") != "https://vanphongdientu.utc.edu.vn/Login":
        parser.error("This runner targets https://vanphongdientu.utc.edu.vn/Login; clear a conflicting BASE_URL")
    os.chdir(ROOT)
    arguments = ["-q", "--tb=short", "--html-report=" + args.html, "--junitxml=reports/utc-live/junit.xml"]
    if args.include_payloads:
        arguments += ["--allow-live-case=" + case for case in ("TC07", "TC08", "TC12")]
    return pytest.main(arguments)


if __name__ == "__main__":
    raise SystemExit(main())
