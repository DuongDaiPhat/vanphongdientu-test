"""Browser creation is called exclusively by the function-scoped fixture."""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService

from e2e.base.settings import Settings


class BaseTest:
    @staticmethod
    def create_driver(settings: Settings):
        options = webdriver.ChromeOptions() if settings.browser == "chrome" else webdriver.EdgeOptions()
        if settings.headless:
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1440,1000")
        if settings.browser_binary:
            options.binary_location = settings.browser_binary
        service_type = ChromeService if settings.browser == "chrome" else EdgeService
        service = service_type(executable_path=settings.driver_path) if settings.driver_path else service_type()
        constructor = webdriver.Chrome if settings.browser == "chrome" else webdriver.Edge
        driver = constructor(service=service, options=options)
        try:
            driver.implicitly_wait(0)
            driver.set_page_load_timeout(settings.page_load_timeout)
        except Exception:
            driver.quit()
            raise
        return driver

    @staticmethod
    def close_driver(driver):
        driver.quit()
