"""Common explicit waits and browser interactions."""

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    def __init__(self, driver, settings):
        self.driver = driver
        self.settings = settings
        self.wait = WebDriverWait(driver, settings.timeout)

    def visible(self, selector):
        return self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, selector)))

    def click(self, selector):
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector))).click()

    def type(self, selector, value):
        element = self.visible(selector)
        element.clear()
        if value:
            element.send_keys(value)
        return element.get_attribute("value")
