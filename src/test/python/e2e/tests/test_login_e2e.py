"""Negative login scenarios TC01-TC22; each ID has its own commit."""

import pytest


@pytest.mark.negative
class TestLoginE2E:

    @pytest.mark.oracle("username", "password")
    def test_tc01_empty_credentials(self, login_page):
        login_page.fill("", "")
        login_page.submit()
        login_page.assert_rejected("username", "password")
