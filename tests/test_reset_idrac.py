from asynctest import patch
from tests.config import ROOT_RESP, SYS_RESP, MAN_RESP, RESET_TYPE_RESP, BOOT_SEQ_RESPONSE_DIRECTOR, RESPONSE_RESET
from tests.test_aiohttp_base import TestBase


class TestResetIdrac(TestBase):
    option_arg = "--racreset"

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_reset_idrac(self, mock_get, mock_post):
        responses = [ROOT_RESP, SYS_RESP, ROOT_RESP, MAN_RESP, RESET_TYPE_RESP]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 204, ["ok"])
        self.boot_seq = BOOT_SEQ_RESPONSE_DIRECTOR
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert RESPONSE_RESET == err
