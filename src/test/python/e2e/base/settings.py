"""Load explicit target-specific oracles; never guess production error text."""

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit


PRODUCTION_HOST = "vanphongdientu.utc.edu.vn"


def load_env(path: Path) -> None:
    """Read plain KEY=VALUE pairs without executing expressions or shell code."""
    if not path.is_file():
        return
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, separator, value = line.partition("=")
        if not separator or not re.fullmatch(r"[A-Z][A-Z0-9_]*", key.strip()):
            raise ValueError(f"Invalid configuration line: {line.partition('=')[0]}")
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1]
        os.environ.setdefault(key.strip(), value)


@dataclass(frozen=True)
class Settings:
    base_url: str
    browser: str
    headless: bool
    timeout: float
    page_load_timeout: float
    report_dir: Path
    environment: str
    driver_path: str
    browser_binary: str
    error_selector: str
    authenticated_selector: str
    patterns: dict[str, str] = field(repr=False)
    known_username: str = field(repr=False)
    known_wrong_password: str = field(repr=False)
    captcha_image_selector: str
    captcha_refresh_selector: str
    captcha_ttl: float
    captcha_ttl_margin: float
    trigger_attempts: int
    max_login_attempts: int
    captcha_single_use: bool
    reset_selector: str
    approved_test_host: str
    assisted_timeout: float

    @classmethod
    def from_env(cls, root: Path) -> "Settings":
        load_env(root / ".env")
        env = os.environ
        def positive(name, default, cast=float, zero=False):
            value = cast(env.get(name) or default)
            if value < 0 or (not zero and value == 0):
                raise ValueError(f"{name} must be {'non-negative' if zero else 'positive'}")
            return value
        def boolean(name, default):
            value = env.get(name, default).lower()
            if value not in {"true", "false"}:
                raise ValueError(f"{name} must be true or false")
            return value == "true"
        url = env.get("BASE_URL", f"https://{PRODUCTION_HOST}/Login")
        parsed = urlsplit(url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("BASE_URL must be an HTTP(S) URL without credentials")
        patterns = {key: env.get(f"{key.upper()}_ERROR_PATTERN", "") for key in ("auth", "username", "password", "captcha")}
        for pattern in patterns.values():
            if pattern:
                re.compile(pattern)
        browser = env.get("BROWSER", "chrome").lower()
        if browser not in {"chrome", "edge"}:
            raise ValueError("BROWSER must be chrome or edge")
        return cls(
            url, browser, boolean("HEADLESS", "true"), positive("TIMEOUT", 10),
            positive("PAGE_LOAD_TIMEOUT", 35), root / env.get("REPORT_DIR", "reports"),
            env.get("ENVIRONMENT", "production"), env.get("DRIVER_PATH", ""), env.get("BROWSER_BINARY", ""),
            env.get("ERROR_SELECTOR", ""), env.get("AUTHENTICATED_SELECTOR", ""), patterns,
            env.get("KNOWN_USERNAME", ""), env.get("KNOWN_WRONG_PASSWORD", ""),
            env.get("CAPTCHA_IMAGE_SELECTOR", ""), env.get("CAPTCHA_REFRESH_SELECTOR", ""),
            positive("CAPTCHA_TTL_SECONDS", 0, zero=True), positive("CAPTCHA_TTL_MARGIN", 1),
            positive("CAPTCHA_TRIGGER_ATTEMPTS", 0, int, zero=True), positive("MAX_LOGIN_ATTEMPTS", 5, int),
            boolean("CAPTCHA_SINGLE_USE", "false"), env.get("RESET_SELECTOR", ""),
            env.get("APPROVED_TEST_HOST", ""), positive("ASSISTED_TIMEOUT", 60),
        )

    def test_environment_allowed(self) -> bool:
        host = urlsplit(self.base_url).hostname
        return self.environment == "test" and host == self.approved_test_host and host != PRODUCTION_HOST
