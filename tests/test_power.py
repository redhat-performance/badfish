from asynctest import patch
from tests.config import (
    INIT_RESP,
    STATE_OFF_RESP,
    BOOT_SEQ_RESPONSE_DIRECTOR,
    RESPONSE_POWER_ON_NOT,
    RESPONSE_POWER_ON_OK,
    RESPONSE_POWER_OFF_NO_STATE,
    RESPONSE_POWER_OFF_ALREADY,
    JOB_OK_RESP,
    RESPONSE_POWER_OFF_MISS_STATE,
)
from tests.test_base import TestBase


class TestPowerOn(TestBase):
    option_arg = "--power-on"

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_power_on_ok(self, mock_get, mock_post):
        responses = INIT_RESP + [STATE_OFF_RESP]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 204, ["ok"])
        self.boot_seq = BOOT_SEQ_RESPONSE_DIRECTOR
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_POWER_ON_OK

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_power_on_not_ok(self, mock_get, mock_post):
        responses = INIT_RESP + [STATE_OFF_RESP]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 409, ["ok"])
        self.boot_seq = BOOT_SEQ_RESPONSE_DIRECTOR
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_POWER_ON_NOT


class TestPowerOff(TestBase):
    option_arg = "--power-off"

    @patch("aiohttp.ClientSession.get")
    def test_power_off_no_state(self, mock_get):
        responses = INIT_RESP
        self.set_mock_response(mock_get, [200, 200, 200, 200, 400], responses)
        self.boot_seq = BOOT_SEQ_RESPONSE_DIRECTOR
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_POWER_OFF_NO_STATE

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_power_off_already(self, mock_get, mock_post):
        responses = INIT_RESP + [STATE_OFF_RESP]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 409, ["ok"])
        self.boot_seq = BOOT_SEQ_RESPONSE_DIRECTOR
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_POWER_OFF_ALREADY

    @patch("aiohttp.ClientSession.get")
    def test_power_miss_state(self, mock_get):
        responses = INIT_RESP + [JOB_OK_RESP]
        self.set_mock_response(mock_get, 200, responses)
        self.boot_seq = BOOT_SEQ_RESPONSE_DIRECTOR
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_POWER_OFF_MISS_STATE
