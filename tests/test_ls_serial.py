from unittest.mock import patch

from tests.config import (
    DELL_REDFISH_ROOT_OEM_RESP,
    EMPTY_OEM_RESP,
    INIT_RESP,
    RESPONSE_LS_SERIAL_NUMBER,
    RESPONSE_LS_SERIAL_SERVICE_TAG,
    RESPONSE_LS_SERIAL_SOMETHING_WRONG,
    RESPONSE_LS_SERIAL_UNSUPPORTED,
    SYSTEM_SERIAL_NUMBER_RESP,
)
from tests.test_base import TestBase


class TestLsSerial(TestBase):
    args = ["--ls-serial"]

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_ls_serial_service_tag(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + [DELL_REDFISH_ROOT_OEM_RESP]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        _, err = self.badfish_call()
        assert err == RESPONSE_LS_SERIAL_SERVICE_TAG

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_ls_serial_serial_number(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + [EMPTY_OEM_RESP, SYSTEM_SERIAL_NUMBER_RESP]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        _, err = self.badfish_call()
        assert err == RESPONSE_LS_SERIAL_NUMBER

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    @patch("badfish.main.Badfish.get_serial_summary")
    def test_ls_serial_unsupported_root(self, mock_get_serial_summary, mock_get, mock_post, mock_delete):
        from badfish.main import BadfishException

        # Mock serial summary to raise the expected exception
        mock_get_serial_summary.side_effect = BadfishException("Server does not support this functionality")

        self.set_mock_response(mock_get, 200, INIT_RESP)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        _, err = self.badfish_call()
        assert err == RESPONSE_LS_SERIAL_UNSUPPORTED

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    @patch("badfish.main.Badfish.get_serial_summary")
    def test_ls_serial_unsupported_systems(self, mock_get_serial_summary, mock_get, mock_post, mock_delete):
        from badfish.main import BadfishException

        # Mock serial summary to raise the expected exception
        mock_get_serial_summary.side_effect = BadfishException("Server does not support this functionality")

        self.set_mock_response(mock_get, 200, INIT_RESP)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        _, err = self.badfish_call()
        assert err == RESPONSE_LS_SERIAL_UNSUPPORTED

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_ls_serial_no_number(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + [EMPTY_OEM_RESP, "{}"]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        _, err = self.badfish_call()
        assert err == RESPONSE_LS_SERIAL_UNSUPPORTED

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_ls_serial_something_wrong(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + [""]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        _, err = self.badfish_call()
        assert err == RESPONSE_LS_SERIAL_SOMETHING_WRONG
