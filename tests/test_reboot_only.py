from asynctest import patch
from tests.config import (
    INIT_RESP,
    STATE_ON_RESP,
    STATE_OFF_RESP,
    RESPONSE_REBOOT_ONLY_SUCCESS,
    BOOT_SEQ_RESPONSE_DIRECTOR,
)
from tests.test_aiohttp_base import TestBase


class TestRebootOnly(TestBase):
    option_arg = "--reboot-only"

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_reboot_only_success(self, mock_get, mock_post):
        responses = INIT_RESP + [STATE_ON_RESP, STATE_OFF_RESP, STATE_ON_RESP]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 204, ["ok"])
        self.boot_seq = BOOT_SEQ_RESPONSE_DIRECTOR
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_REBOOT_ONLY_SUCCESS
