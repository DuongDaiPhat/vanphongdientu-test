"""Read-only Selenium locator verification; does not submit credentials."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/test/python"))

from selenium.webdriver.common.by import By

from e2e.base.base_test import BaseTest
from e2e.base.settings import Settings
from e2e.pages.login_page import LoginPage


def main():
    settings = Settings.from_env(ROOT)
    settings.report_dir.mkdir(parents=True, exist_ok=True)
    driver = BaseTest.create_driver(settings)
    results = {"target": settings.base_url, "fields": {}, "read_only": True}
    try:
        driver.get(settings.base_url)
        page = LoginPage(driver, settings)
        page.visible(page.FORM)
        results["captcha_visible"] = page.captcha_visible()
        for field, (name, kind, placeholder) in page.FIELDS.items():
            if field == "captcha" and not results["captcha_visible"]:
                results["fields"][field] = {"status": "SKIPPED", "reason": "CAPTCHA absent in this session"}
                continue
            selector = page.selector_for(field)
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            attributes = [{key: el.get_attribute(key) for key in ("name", "type", "placeholder")} for el in elements]
            passed = len(elements) == 1 and attributes[0] == {"name": name, "type": kind, "placeholder": placeholder}
            results["fields"][field] = {"selector": selector, "match_count": len(elements), "attributes": attributes, "status": "PASS" if passed else "FAIL"}
        results["browser_version"] = driver.capabilities.get("browserVersion")
        results["captcha_semantically_present"] = bool(driver.find_elements(By.CSS_SELECTOR, page.FORM + " input[name='captcha']"))
        driver.save_screenshot(str(settings.report_dir / "locator-probe.png"))
    finally:
        driver.quit()
    path = settings.report_dir / "locator-probe.json"
    path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(results, ensure_ascii=True, indent=2))
    return 0 if all(row["status"] != "FAIL" for row in results["fields"].values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
