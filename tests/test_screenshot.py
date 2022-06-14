import os
import pytest

from asynctest import patch, CoroutineMock
from tests.config import (
    INIT_RESP,
    SCREENSHOT_RESP,
    IMAGE_SAVED,
    SCREENSHOT_NAME,
    GIF_NAME,
    SCREENSHOT_NOT_SUPPORTED,
    SCREENSHOT_BAD_REQUEST,
    SCREENSHOT_GIF_FALSE_OK,
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


class TestGif(TestBase):
    option_arg = "--gif"

    @patch("PIL.Image.open")
    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_gif_ok(self, mock_get, mock_post, mock_delete, mock_img):
        mock_img.return_value.__aenter__.return_value = CoroutineMock()

        self.set_mock_response(mock_get, 200, INIT_RESP)
        self.set_mock_response(mock_post, 200, SCREENSHOT_RESP)
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg]

        with patch("time.strftime", return_value="now"):
            _, err = self.badfish_call()

        assert err == IMAGE_SAVED % GIF_NAME

    @patch("PIL.Image.open")
    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_gif_bad_request(self, mock_get, mock_post, mock_delete, mock_img):
        mock_img.return_value.__aenter__.return_value = CoroutineMock()

        self.set_mock_response(mock_get, 200, INIT_RESP)
        post_responses = ["OK", "", "", SCREENSHOT_RESP, SCREENSHOT_RESP]
        self.set_mock_response(
            mock_post, [200, 400, 400, 200, 200], post_responses, True
        )
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg]

        with patch("time.strftime", return_value="now"):
            _, err = self.badfish_call()

        assert err == SCREENSHOT_GIF_FALSE_OK


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
        assert err == SCREENSHOT_GIF_FALSE_OK
