from asynctest import patch
from tests.config import (
    INIT_RESP, POWER_CONSUMED_RESP, RESPONSE_POWER_CONSUMED_OK, RESPONSE_POWER_CONSUMED_404,

)
from tests.test_base import  TestBase

class TestPowerConsumed(TestBase):
    args = ["--get-power-consumed"]

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_power_consumed(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + [POWER_CONSUMED_RESP]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK", True)
        self.set_mock_response(mock_delete, 200, "OK")
        _, err = self.badfish_call()
        assert err == RESPONSE_POWER_CONSUMED_OK

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_power_consumed_404(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + [POWER_CONSUMED_RESP]
        self.set_mock_response(mock_get,[200,200,200,200,200,404], responses)
        self.set_mock_response(mock_post, 200, "OK", True)
        self.set_mock_response(mock_delete, 200, "OK")
        _, err = self.badfish_call()
        assert err == RESPONSE_POWER_CONSUMED_404
