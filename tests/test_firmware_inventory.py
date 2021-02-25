from asynctest import patch
from tests.config import (
    INIT_RESP,
    FIRMWARE_INVENTORY_RESP,
    FIRMWARE_INVENTORY_1_RESP,
    FIRMWARE_INVENTORY_2_RESP,
    RESPONSE_FIRMWARE_INVENTORY,
)
from tests.test_base import TestBase


class TestJobQueue(TestBase):
    option_arg = "--firmware-inventory"

    @patch("aiohttp.ClientSession.get")
    def test_ls_jobs(self, mock_get):
        responses_add = [
            FIRMWARE_INVENTORY_RESP,
            FIRMWARE_INVENTORY_1_RESP,
            FIRMWARE_INVENTORY_2_RESP
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_FIRMWARE_INVENTORY
