from unittest.mock import patch

from tests.config import BOOT_SEQ_RESPONSE_DIRECTOR, INIT_RESP, RESET_TYPE_RESP, RESPONSE_RESET, RESPONSE_RESET_FAIL
from tests.test_base import TestBase


class TestResetBios(TestBase):
    option_arg = "--factory-reset"

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_reset_bios(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + [RESET_TYPE_RESP]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, [200, 204], "OK", True)
        self.set_mock_response(mock_delete, 200, "OK")
        self.boot_seq = BOOT_SEQ_RESPONSE_DIRECTOR
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_RESET % ("204", "BIOS", "BIOS")

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_reset_bios_fail(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + [RESET_TYPE_RESP]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, [200, 400], ["OK", "Bad Request"], True)
        self.set_mock_response(mock_delete, 200, "OK")
        self.boot_seq = BOOT_SEQ_RESPONSE_DIRECTOR
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_RESET_FAIL
