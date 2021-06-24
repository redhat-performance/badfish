from asynctest import patch
from tests.config import (
    INIT_RESP,
    MEMORY_MEMBERS_RESP,
    MEMORY_SUMMARY_RESP,
    MEMORY_A5_RESP,
    MEMORY_B2_RESP,
    RESPONSE_LS_MEMORY,
)
from tests.test_base import TestBase


class TestLsMemory(TestBase):
    option_arg = "--ls-memory"

    @patch("aiohttp.ClientSession.get")
    def test_ls_memory(self, mock_get):
        responses_add = [
            MEMORY_SUMMARY_RESP,
            MEMORY_MEMBERS_RESP,
            MEMORY_A5_RESP,
            MEMORY_B2_RESP
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_LS_MEMORY
