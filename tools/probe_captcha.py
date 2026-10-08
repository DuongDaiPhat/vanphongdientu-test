"""Bounded CAPTCHA discovery using one synthetic account; never solve a challenge."""

import argparse
import json
import re
import sys
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/test/python"))

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from e2e.base.base_test import BaseTest
from e2e.base.settings import Settings, load_env
from e2e.pages.login_page import LoginPage


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observe-empty", action="store_true", help="Submit an empty CAPTCHA once to observe its validation message")
    args = parser.parse_args()
    load_env(ROOT / "config/utc.env")
    settings = Settings.from_env(ROOT)
    if settings.base_url != "https://vanphongdientu.utc.edu.vn/Login":
        raise SystemExit("This bounded discovery is authorized only for UTC Login")
    settings.report_dir.mkdir(parents=True, exist_ok=True)
    driver = BaseTest.create_driver(settings)
    data = {"target": settings.base_url, "attempts": [], "submission_budget": min(5, settings.max_login_attempts)}
    try:
        page = LoginPage(driver, settings).open()
        username = "qa_invalid_" + uuid4().hex[:16]
        for index in range(data["submission_budget"]):
            if page.captcha_visible():
                break
            page.fill(username, "InvalidPass_123!")
            page.submit()
            page.wait.until(EC.staleness_of(page._previous_form))
            page.visible(page.FORM)
            error = page.error_text()
            visible = page.captcha_visible()
            data["attempts"].append({"number": index + 1, "error": error, "captcha_visible": visible})
            print(json.dumps(data["attempts"][-1], ensure_ascii=True), flush=True)
            if visible or not re.search(settings.patterns["auth"], error):
                break
        data["captcha_visible"] = page.captcha_visible()
        if data["captcha_visible"] and args.observe_empty:
            page.fill(username, "InvalidPass_123!", captcha="")
            page.submit()
            page.wait.until(EC.staleness_of(page._previous_form))
            page.visible(page.FORM)
            data["empty_captcha_error"] = page.error_text()
        data["elements"] = [
            {"tag": e.tag_name, "text": e.text, "id": e.get_attribute("id"), "name": e.get_attribute("name"),
             "type": e.get_attribute("type"), "src": e.get_attribute("src"), "href": e.get_attribute("href"),
             "onclick": e.get_attribute("onclick")}
            for e in driver.find_elements(By.CSS_SELECTOR, page.FORM + " input, " + page.FORM + " img, " + page.FORM + " a, " + page.FORM + " span")
            if e.is_displayed()
        ]
        driver.save_screenshot(str(settings.report_dir / "captcha-discovery.png"))
    finally:
        driver.quit()
    path = settings.report_dir / "captcha-discovery.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Discovery evidence: " + str(path), flush=True)


if __name__ == "__main__":
    main()
