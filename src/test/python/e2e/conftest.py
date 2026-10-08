"""Environment gates, browser fixtures, explicit CAPTCHA assistance and reports."""

import json
import queue
import re
import threading
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest

from e2e.base.base_test import BaseTest
from e2e.base.settings import Settings
from e2e.pages.login_page import LoginPage


def pytest_addoption(parser):
    parser.addoption("--allow-test-env", action="store_true", help="Enable gated tests on an explicitly configured test host")
    parser.addoption("--allow-assisted", action="store_true", help="Enable manual CAPTCHA entry; run with -s")
    parser.addoption("--captcha-inbox", default="", help="Directory for session-specific human CAPTCHA requests and answers")
    parser.addoption("--prepare-captcha", action="store_true", help="Use bounded invalid synthetic logins to obtain a real CAPTCHA before CAPTCHA cases")
    parser.addoption("--demo", action="store_true", help="Verify the suite on an isolated local reference form, not UTC")
    parser.addoption("--demo-defect", choices=["none", "captcha-bypass", "authentication-bypass", "wrong-message"], default="none")
    parser.addoption("--html-report", default="", help="Write a self-contained HTML report to this path")
    parser.addoption("--allow-live-case", action="append", choices=["TC07", "TC08", "TC12", "TC22"], default=[], help="Explicitly enable one bounded case on the live target")


def pytest_configure(config):
    config.addinivalue_line("markers", "oracle(*categories): Required observed error categories")
    config.addinivalue_line("markers", "requires(*fields): Required settings values")
    config._login_rows = []
    config._login_durations = {}
    config._login_started = datetime.now(timezone.utc).isoformat()
    root = Path(str(config.rootpath))
    try:
        if config.getoption("--demo"):
            from e2e.base.reference_server import ReferenceServer
            server = ReferenceServer(config.getoption("--demo-defect"))
            server.start()
            config._demo_server = server
            config._login_settings = server.settings(root)
        else:
            config._login_settings = Settings.from_env(root)
    except (ValueError, re.error) as error:
        raise pytest.UsageError(str(error)) from error
    config._login_settings.report_dir.mkdir(parents=True, exist_ok=True)
    config._login_run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "-" + uuid4().hex[:6]


def pytest_collection_modifyitems(config, items):
    settings = config._login_settings
    demo = config.getoption("--demo")
    for item in items:
        reasons = []
        case = re.search(r"tc\d{2}", item.name, re.I)
        live_allowed = case is not None and case.group().upper() in config.getoption("--allow-live-case")
        if item.get_closest_marker("test_env_only") and not (demo or live_allowed or (config.getoption("--allow-test-env") and settings.test_environment_allowed())):
            reasons.append("requires --allow-test-env, ENVIRONMENT=test and APPROVED_TEST_HOST matching a non-production target")
        if item.get_closest_marker("assisted") and not (demo or config.getoption("--allow-assisted")):
            reasons.append("requires CAPTCHA assistance (--allow-assisted -s or an official test provider)")
        requires = item.get_closest_marker("requires")
        if requires:
            missing = [name for name in requires.args if not getattr(settings, name)]
            if missing:
                reasons.append("missing confirmed settings: " + ", ".join(missing))
        if reasons:
            item.add_marker(pytest.mark.skip(reason="BLOCKED: " + "; ".join(reasons)))


@pytest.fixture
def settings(request):
    return request.config._login_settings


@pytest.fixture
def credentials(request):
    # Only synthetic values are recorded; confirmed account data is never logged.
    values = ("qa_invalid_" + uuid4().hex[:16], "InvalidPass_123!")
    request.node._synthetic_data = {"username": values[0], "password": values[1]}
    return values


@pytest.fixture
def driver(request, settings):
    browser = BaseTest.create_driver(settings)
    request.node._login_driver = browser
    try:
        yield browser
    finally:
        BaseTest.close_driver(browser)


@pytest.fixture
def login_page(request, driver, settings):
    page = LoginPage(driver, settings)
    page.fresh_browser = True  # The driver fixture always creates an isolated browser.
    request.node._login_page = page
    if request.config.getoption("--demo"):
        url = request.config._demo_server.url_for(request.node.name)
    else:
        url = settings.base_url
    page.open(url)
    needs_captcha = bool(request.node.get_closest_marker("captcha"))
    preparation = []
    if needs_captcha and request.config.getoption("--prepare-captcha") and not request.config.getoption("--demo"):
        if not settings.patterns.get("auth") or not settings.error_selector:
            pytest.skip("BLOCKED: CAPTCHA preparation requires a verified authentication error")
        username = "qa_invalid_" + uuid4().hex[:16]
        for number in range(1, min(5, settings.max_login_attempts) + 1):
            if page.captcha_visible():
                break
            page.fill(username, "InvalidPass_123!")
            page.submit()
            page.assert_rejected("auth", require_server=True)
            preparation.append({"attempt": number, "error": page.error_text(), "captcha_visible": page.captcha_visible()})
        request.node._captcha_preparation = preparation
    visible = page.captcha_visible()
    prerequisites = request.node.get_closest_marker("requires")
    resets_session = prerequisites is not None and ("reset_selector" in prerequisites.args or "reset_strategy" in prerequisites.args)
    if needs_captcha and not visible:
        pytest.skip("SKIPPED: CAPTCHA is not visible in this fresh session")
    if not needs_captcha and visible and not resets_session:
        pytest.skip("SKIPPED: basic case requires CAPTCHA absent; CAPTCHA is visible")
    oracle = request.node.get_closest_marker("oracle")
    if oracle:
        missing = [name for name in oracle.args if not settings.patterns.get(name)]
        if missing or not settings.error_selector:
            pytest.skip("BLOCKED: unverified error oracle: " + ", ".join(missing or ["ERROR_SELECTOR"]))
    return page


@pytest.fixture
def captcha_solver(request, settings):
    def solve(page, *, valid=True):
        if request.config.getoption("--demo"):
            return request.config._demo_server.code_for(page, valid=valid)
        if not request.config.getoption("--allow-assisted") or request.config.getoption("capture") != "no":
            pytest.skip("BLOCKED: CAPTCHA entry requires --allow-assisted -s or a test provider fixture")
        inbox = request.config.getoption("--captcha-inbox")
        if inbox:
            from e2e.base.captcha_assistance import wait_for_code
            try:
                code = wait_for_code(page, inbox, request.node.name, settings.assisted_timeout)
            except TimeoutError:
                pytest.skip("BLOCKED: CAPTCHA assistance timed out for the current challenge")
            return code if valid else ("0" if code[0] != "0" else "1") + code[1:]
        image_path = settings.report_dir / (request.config._login_run_id + "-captcha.png")
        page.driver.save_screenshot(str(image_path))
        print(f"\nCAPTCHA assistance for {request.node.name}; inspect {image_path}")
        answer = queue.Queue()
        def read_answer():
            try:
                answer.put(input("Enter the CURRENT correct CAPTCHA code (blank cancels): ").strip())
            except (EOFError, OSError):
                answer.put("")
        threading.Thread(target=read_answer, daemon=True).start()
        try:
            code = answer.get(timeout=settings.assisted_timeout)
        except queue.Empty:
            pytest.skip("BLOCKED: CAPTCHA assistance timed out")
        if not code:
            pytest.skip("BLOCKED: no confirmed CAPTCHA code supplied")
        # Same length, certainly different, without relying on a random guess.
        return code if valid else ("0" if code[0] != "0" else "1") + code[1:]
    return solve


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    config = item.config
    config._login_durations[item.nodeid] = config._login_durations.get(item.nodeid, 0) + report.duration
    if report.when == "setup" and report.passed:
        return
    if report.when == "teardown" and not report.failed:
        return
    match = re.search(r"tc\d{2}", item.name, re.I)
    reason = str(report.longrepr) if report.longrepr else ""
    status = "BLOCKED" if report.skipped and "BLOCKED:" in reason else "SKIPPED" if report.skipped else "PASS" if report.passed else "FAIL"
    row = {"id": match.group().upper() if match else item.name, "test": item.nodeid, "phase": report.when, "status": status, "reason": reason, "duration_seconds": report.duration, "synthetic_data": getattr(item, "_synthetic_data", {}), "evidence": []}
    if hasattr(item, "_captcha_preparation"):
        row["captcha_preparation"] = item._captcha_preparation
    browser = getattr(item, "_login_driver", None)
    page = getattr(item, "_login_page", None)
    if page:
        row["observed"] = getattr(page, "last_observation", {})
        row["input"] = getattr(page, "last_input", {})
        try:
            row["captcha_visible"] = page.captcha_visible()
        except Exception:
            row["captcha_visible"] = None
    if browser:
        row["browser"] = browser.capabilities.get("browserName")
        row["browser_version"] = browser.capabilities.get("browserVersion")
    if browser and (report.failed or config.getoption("--html-report")):
        path = config._login_settings.report_dir / (config._login_run_id + "-" + re.sub(r"[^\w.-]", "_", item.name) + "-" + report.when + ".png")
        try:
            browser.save_screenshot(str(path))
            row["evidence"].append(str(path))
        except Exception as error:
            row["evidence_error"] = type(error).__name__
    # A teardown failure replaces the PASS rather than increasing the case count.
    config._login_rows = [existing for existing in config._login_rows if existing["test"] != row["test"]]
    config._login_rows.append(row)


def pytest_sessionfinish(session, exitstatus):
    config = session.config
    settings = config._login_settings
    for row in config._login_rows:
        row["duration_seconds"] = config._login_durations.get(row["test"], row["duration_seconds"])
    data = {"run_id": config._login_run_id, "started_utc": config._login_started, "finished_utc": datetime.now(timezone.utc).isoformat(), "target": settings.base_url, "environment": settings.environment, "demo": config.getoption("--demo"), "exit_code": int(exitstatus), "collected": session.testscollected, "counts": dict(Counter(row["status"] for row in config._login_rows)), "results": config._login_rows}
    path = settings.report_dir / (config._login_run_id + "-results.json")
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# Login test execution", "", f"Target: {settings.base_url}", f"Reference form only: {data['demo']}", f"Started UTC: {data['started_utc']}", "", "| ID / variant | Status | Phase | Reason |", "| --- | --- | --- | --- |"]
    for row in data["results"]:
        reason = row["reason"].replace("|", "\\|").replace("\n", "<br>")
        lines.append(f"| {row['test'].split('::')[-1]} | {row['status']} | {row['phase']} | {reason} |")
    path.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if config.getoption("--html-report"):
        from e2e.base.html_report import write_html_report
        destination = Path(config.getoption("--html-report"))
        if not destination.is_absolute():
            destination = Path(str(config.rootpath)) / destination
        write_html_report(data, destination)


def pytest_unconfigure(config):
    server = getattr(config, "_demo_server", None)
    if server:
        server.stop()
