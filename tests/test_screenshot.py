import os
from unittest.mock import patch

import pytest

from tests.config import (
    IMAGE_SAVED,
    INIT_RESP,
    SCREENSHOT_BAD_REQUEST,
    SCREENSHOT_FALSE_OK,
    SCREENSHOT_NAME,
    SCREENSHOT_NOT_SUPPORTED,
    SCREENSHOT_RESP,
)
from tests.test_base import TestBase


class TestScreenshot(TestBase):
    option_arg = "--screenshot"

    @pytest.fixture(scope="function", autouse=True)
    def teardown(self, request):
        def remove_file():
            os.remove(SCREENSHOT_NAME)

        request.addfinalizer(remove_file)

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_screenshot_ok(self, mock_get, mock_post, mock_delete):

        self.set_mock_response(mock_get, 200, INIT_RESP)
        self.set_mock_response(mock_post, 200, SCREENSHOT_RESP)
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg]

        with patch("time.strftime", return_value="now"):
            _, err = self.badfish_call()

        assert err == IMAGE_SAVED % SCREENSHOT_NAME


class TestScreenshotErrors(TestBase):
    option_arg = "--screenshot"

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_screenshot_not_supported(self, mock_get, mock_post, mock_delete):
        self.set_mock_response(mock_get, 200, INIT_RESP)
        self.set_mock_response(mock_post, [200, 404], ["OK", "Not Found"], True)
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == SCREENSHOT_NOT_SUPPORTED

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_screenshot_bad_request(self, mock_get, mock_post, mock_delete):
        self.set_mock_response(mock_get, 200, INIT_RESP)
        self.set_mock_response(mock_post, [200, 400], ["OK", SCREENSHOT_RESP], True)
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == SCREENSHOT_BAD_REQUEST

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_screenshot_false_ok(self, mock_get, mock_post, mock_delete):
        self.set_mock_response(mock_get, 200, INIT_RESP)
        self.set_mock_response(mock_post, [200, 200], ["OK", ""], True)
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == SCREENSHOT_FALSE_OK
