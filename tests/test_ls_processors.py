from asynctest import patch
from tests.config import (
    INIT_RESP,
    PROCESSOR_MEMBERS_RESP,
    PROCESSOR_CPU_RESP,
    PROCESSOR_SUMMARY_RESP,
    RESPONSE_LS_PROCESSORS,
)
from tests.test_base import TestBase


class TestLsMemory(TestBase):
    option_arg = "--ls-processors"

    @patch("aiohttp.ClientSession.get")
    def test_ls_memory(self, mock_get):
        responses_add = [
            PROCESSOR_SUMMARY_RESP,
            PROCESSOR_MEMBERS_RESP,
            PROCESSOR_CPU_RESP % ("1", "1"),
            PROCESSOR_CPU_RESP % ("2", "2"),
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_LS_PROCESSORS
