from asynctest import patch
from tests.config import (
    RESET_TYPE_RESP,
    BOOT_SEQ_RESPONSE_DIRECTOR,
    RESPONSE_RESET,
    INIT_RESP,
)
from tests.test_base import TestBase


class TestResetBios(TestBase):
    option_arg = "--factory-reset"

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_reset_bios(self, mock_get, mock_post):
        responses = INIT_RESP + [RESET_TYPE_RESP]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 204, ["ok"])
        self.boot_seq = BOOT_SEQ_RESPONSE_DIRECTOR
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_RESET % ("BIOS", "BIOS")
