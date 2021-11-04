import os
import pytest

from asynctest import patch
from tests.config import (
    INIT_RESP,
    SCREENSHOT_RESP,
    SCREENSHOT_OK,
    SCREENSHOT_NAME,
)
from tests.test_base import TestBase


class TestScreenshot(TestBase):
    option_arg = "--screenshot"

    @pytest.fixture(scope="function", autouse=True)
    def teardown(self, request):
        def remove_file():
            os.remove(SCREENSHOT_NAME)

        request.addfinalizer(remove_file)

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_screenshot_ok(self, mock_get, mock_post):

        self.set_mock_response(mock_get, 200, INIT_RESP)
        self.set_mock_response(mock_post, 200, SCREENSHOT_RESP)
        self.args = [self.option_arg]

        with patch("time.strftime", return_value="now"):
            _, err = self.badfish_call()

        assert err == SCREENSHOT_OK
