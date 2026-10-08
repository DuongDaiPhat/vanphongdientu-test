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
