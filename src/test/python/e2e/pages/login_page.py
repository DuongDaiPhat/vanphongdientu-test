"""Verified attribute locators and observable rejection assertions."""

import re
import time

import pytest
from selenium.common.exceptions import NoAlertPresentException, StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from e2e.pages.base_page import BasePage


class LocatorMismatch(AssertionError):
    """A locator does not uniquely identify its intended field."""


class LoginPage(BasePage):
    FORM = "form[action='/Login'][method='post']"
    USERNAME = FORM + " input[name='username'][type='text']"
    PASSWORD = FORM + " input[name='userpwd'][type='password']"
    CAPTCHA = FORM + " input[name='captcha'][type='text']"
    SUBMIT = FORM + " > input.submit_login[type='submit']"
    FIELDS = {
        "username": ("username", "text", "Tên đăng nhập"),
        "password": ("userpwd", "password", "Mật khẩu"),
        "captcha": ("captcha", "text", "Mã bảo mật"),
    }

    def open(self, url=None):
        self.driver.get(url or self.settings.base_url)
        self.visible(self.FORM)
        self.verify_field("username")
        self.verify_field("password")
        self.captcha_visible()
        return self

    def selector_for(self, field):
        if field == "captcha":
            return self.CAPTCHA
        return getattr(self, field.upper())

    def verify_field(self, field):
        selector = self.selector_for(field)
        name, kind, placeholder = self.FIELDS[field]
        matches = self.driver.find_elements(By.CSS_SELECTOR, selector)
        if len(matches) != 1:
            raise LocatorMismatch(f"{field}: CSS selector matched {len(matches)} elements; expected exactly one: {selector}")
        element = matches[0]
        actual = tuple(element.get_attribute(attr) for attr in ("name", "type", "placeholder"))
        if actual != (name, kind, placeholder):
            raise LocatorMismatch(f"{field}: selector identifies attributes {actual!r}, expected {(name, kind, placeholder)!r}")
        return element

    def captcha_visible(self):
        # Visibility determines whether this session can run CAPTCHA scenarios.
        semantic = self.driver.find_elements(By.CSS_SELECTOR, self.FORM + " input[name='captcha']")
        if not any(element.is_displayed() for element in semantic):
            return False
        return self.verify_field("captcha").is_displayed()

    def fill(self, username, password, captcha=None):
        self.verify_field("username")
        self.verify_field("password")
        actual = {"username": self.type(self.selector_for("username"), username), "password": self.type(self.selector_for("password"), password)}
        if captcha is not None:
            self.verify_field("captcha")
            actual["captcha"] = self.type(self.CAPTCHA, captcha)
        self.last_input = dict(actual)
        if username == self.settings.known_username and self.settings.known_username:
            self.last_input.update(username="<confirmed test account>", password="<configured wrong password>")
        if captcha:
            self.last_input["captcha"] = "<supplied CAPTCHA code>"
        return actual

    def submit(self, enter=False):
        self._previous_form = self.driver.find_element(By.CSS_SELECTOR, self.FORM)
        self._previous_errors = self.error_text()
        if enter:
            self.visible(self.selector_for("password")).send_keys(Keys.ENTER)
        else:
            self.click(self.SUBMIT)

    def error_text(self):
        if not self.settings.error_selector:
            return ""
        return "\n".join(e.text for e in self.driver.find_elements(By.CSS_SELECTOR, self.settings.error_selector) if e.is_displayed()).strip()

    def assert_rejected(self, *categories, require_server=False):
        """Only accept a new response with the specific expected error, or native validation."""
        def rejection_observed(_driver):
            try:
                self.driver.switch_to.alert
            except NoAlertPresentException:
                pass
            else:
                raise AssertionError("Unexpected JavaScript alert during login rejection")
            if self.settings.authenticated_selector:
                assert not any(e.is_displayed() for e in self.driver.find_elements(By.CSS_SELECTOR, self.settings.authenticated_selector)), "Authenticated content appeared after a negative login"
            native = False
            if not require_server:
                for category in categories:
                    if category in self.FIELDS:
                        element = self.verify_field(category)
                        if element.is_displayed() and self.driver.execute_script("return !arguments[0].validity.valid && !!arguments[0].validationMessage;", element):
                            native = True
            try:
                self._previous_form.is_enabled()
                new_document = False
            except StaleElementReferenceException:
                new_document = True
            text = self.error_text()
            new_response = new_document or text != self._previous_errors
            matches = any(self.settings.patterns.get(category) and re.search(self.settings.patterns[category], text, re.I) for category in categories)
            if not native and not (new_response and matches):
                return False
            rejected = any(e.is_displayed() for e in self.driver.find_elements(By.CSS_SELECTOR, self.FORM))
            if rejected:
                self.last_observation = {"error_text": text, "expected_categories": list(categories), "native_validation": native, "new_response": new_response, "login_form_visible": True, "url": self.driver.current_url}
            return rejected
        self.wait.until(rejection_observed, message=f"No new rejection matching categories {categories}; last error: {self.error_text()!r}")

    def assert_no_server_details(self):
        text = self.driver.find_element(By.TAG_NAME, "body").text
        assert not re.search(r"SQLSTATE|Traceback \(most recent call last\)|Stack trace:|Fatal error:|Internal Server Error", text, re.I), "Server implementation details or server error exposed"

    def challenge_identity(self):
        if not self.settings.captcha_image_selector:
            pytest.skip("BLOCKED: CAPTCHA_IMAGE_SELECTOR has not been verified")
        image = self.visible(self.settings.captcha_image_selector)
        return image.get_attribute("src") or image.screenshot_as_base64

    def refresh_challenge(self):
        if not self.settings.captcha_refresh_selector:
            pytest.skip("BLOCKED: CAPTCHA_REFRESH_SELECTOR has not been verified")
        previous = self.challenge_identity()
        self.click(self.settings.captcha_refresh_selector)
        self.wait.until(lambda _: self.challenge_identity() != previous, "CAPTCHA challenge identity did not change after refresh")
        self.verify_field("captcha")

    def wait_for_expiry(self):
        seconds = self.settings.captcha_ttl + self.settings.captcha_ttl_margin
        if self.settings.captcha_ttl <= 0:
            pytest.skip("BLOCKED: CAPTCHA TTL has not been confirmed")
        deadline = time.monotonic() + seconds
        WebDriverWait(self.driver, seconds + 2, poll_frequency=0.2).until(lambda _: time.monotonic() >= deadline)

    def reset_attempts(self):
        if not self.settings.reset_selector:
            pytest.skip("BLOCKED: RESET_SELECTOR is required for the test environment")
        previous = self.driver.find_element(By.CSS_SELECTOR, self.FORM)
        self.click(self.settings.reset_selector)
        self.wait.until(EC.staleness_of(previous), "Reset did not reload the form")
        self.verify_field("username")
        self.verify_field("password")
