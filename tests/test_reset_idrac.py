from asynctest import patch
from tests.config import (
    RESET_TYPE_RESP,
    BOOT_SEQ_RESPONSE_DIRECTOR,
    RESPONSE_RESET,
    INIT_RESP, RESPONSE_RESET_FAIL,
)
from tests.test_base import TestBase


class TestResetIdrac(TestBase):
    option_arg = "--racreset"

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_reset_idrac(self, mock_get, mock_post):
        responses = INIT_RESP + [RESET_TYPE_RESP]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 204, ["ok"])
        self.boot_seq = BOOT_SEQ_RESPONSE_DIRECTOR
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_RESET % ("iDRAC", "iDRAC")

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_reset_idrac_fail(self, mock_get, mock_post):
        responses = INIT_RESP + [RESET_TYPE_RESP]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 400, "not_ok")
        self.boot_seq = BOOT_SEQ_RESPONSE_DIRECTOR
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_RESET_FAIL
