"""Negative login scenarios TC01-TC22; each ID has its own commit."""

import pytest


@pytest.mark.negative
class TestLoginE2E:

    @pytest.mark.oracle("username", "password")
    def test_tc01_empty_credentials(self, login_page):
        login_page.fill("", "")
        login_page.submit()
        login_page.assert_rejected("username", "password")

    @pytest.mark.oracle("username")
    def test_tc02_missing_username(self, login_page, credentials):
        login_page.fill("", credentials[1])
        login_page.submit()
        login_page.assert_rejected("username")

    @pytest.mark.oracle("password")
    def test_tc03_missing_password(self, login_page, credentials):
        login_page.fill(credentials[0], "")
        login_page.submit()
        login_page.assert_rejected("password")

    @pytest.mark.oracle("auth")
    def test_tc04_invalid_credentials(self, login_page, credentials):
        login_page.fill(*credentials)
        login_page.submit()
        login_page.assert_rejected("auth", require_server=True)

    @pytest.mark.oracle("auth")
    @pytest.mark.requires("known_username", "known_wrong_password")
    def test_tc05_existing_username_wrong_password(self, login_page, settings):
        login_page.fill(settings.known_username, settings.known_wrong_password)
        login_page.submit()
        login_page.assert_rejected("auth", require_server=True)

    @pytest.mark.oracle("auth")
    def test_tc06_padded_username(self, login_page, credentials):
        login_page.fill("  " + credentials[0] + "  ", credentials[1])
        login_page.submit()
        login_page.assert_rejected("auth", require_server=True)

    @pytest.mark.security
    @pytest.mark.test_env_only
    @pytest.mark.oracle("auth")
    def test_tc07_sql_payload(self, login_page):
        payload = "' OR '1'='1"
        login_page.fill(payload, payload)
        login_page.submit()
        login_page.assert_rejected("auth", require_server=True)
        login_page.assert_no_server_details()

    @pytest.mark.security
    @pytest.mark.test_env_only
    @pytest.mark.oracle("auth")
    def test_tc08_xss_payload(self, login_page, credentials):
        login_page.fill("<script>alert('qa_xss')</script>", credentials[1])
        login_page.submit()
        login_page.assert_rejected("auth", require_server=True)
        login_page.assert_no_server_details()

    @pytest.mark.oracle("auth")
    def test_tc09_enter_submission(self, login_page, credentials):
        login_page.fill(*credentials)
        login_page.submit(enter=True)
        login_page.assert_rejected("auth", require_server=True)

    @pytest.mark.oracle("username", "auth")
    def test_tc10_whitespace_username(self, login_page, credentials):
        login_page.fill("   ", credentials[1])
        login_page.submit()
        login_page.assert_rejected("username", "auth")

    @pytest.mark.oracle("password", "auth")
    def test_tc11_whitespace_password(self, login_page, credentials):
        login_page.fill(credentials[0], "   ")
        login_page.submit()
        login_page.assert_rejected("password", "auth")

    @pytest.mark.test_env_only
    @pytest.mark.oracle("username", "auth")
    def test_tc12_long_username(self, login_page, credentials, request):
        actual = login_page.fill("a" * 256, credentials[1])
        request.node._synthetic_data["actual_username_length"] = len(actual["username"])
        login_page.submit()
        login_page.assert_rejected("username", "auth")
        login_page.assert_no_server_details()

    @pytest.mark.captcha
    @pytest.mark.oracle("captcha")
    def test_tc13_empty_captcha(self, login_page, credentials):
        login_page.fill(*credentials, captcha="")
        login_page.submit()
        login_page.assert_rejected("captcha")
