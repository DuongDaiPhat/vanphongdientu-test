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
    parser.add_argument("--cases", nargs="+", choices=[f"TC{number:02}" for number in range(1, 23)], help="Run only these IDs; omitted IDs are deselected, never reported as PASS")
    parser.add_argument("--assisted", action="store_true", help="Allow a human to enter CAPTCHA answers")
    parser.add_argument("--captcha-inbox", default="", help="Receive human answers through challenge-specific JSON files (requires --assisted)")
    parser.add_argument("--prepare-captcha", action="store_true", help="Prepare CAPTCHA cases using at most five invalid synthetic logins per fresh session")
    parser.add_argument("--check-activation", action="store_true", help="Enable bounded TC22 using a confirmed threshold and reset strategy")
    args = parser.parse_args()
    if args.captcha_inbox and not args.assisted:
        parser.error("--captcha-inbox requires --assisted")
    load_env(ROOT / "config/utc.env")
    if os.environ.get("BASE_URL") != "https://vanphongdientu.utc.edu.vn/Login":
        parser.error("This runner targets https://vanphongdientu.utc.edu.vn/Login; clear a conflicting BASE_URL")
    os.chdir(ROOT)
    arguments = ["-q", "--tb=short", "--html-report=" + args.html, "--junitxml=reports/utc-live/junit.xml"]
    if args.include_payloads:
        arguments += ["--allow-live-case=" + case for case in ("TC07", "TC08", "TC12")]
    if args.cases:
        arguments += ["-k", " or ".join("test_" + case.lower() + "_" for case in args.cases)]
    if args.assisted:
        arguments += ["--allow-assisted", "-s"]
    if args.captcha_inbox:
        arguments += ["--captcha-inbox=" + args.captcha_inbox]
    if args.prepare_captcha:
        arguments += ["--prepare-captcha"]
    if args.check_activation:
        arguments += ["--allow-live-case=TC22"]
    return pytest.main(arguments)


if __name__ == "__main__":
    raise SystemExit(main())
