from unittest.mock import patch

from tests.config import (
    BOOT_SEQ_RESPONSE_DIRECTOR,
    INIT_RESP,
    JOB_OK_RESP,
    RESPONSE_POWER_OFF_ALREADY,
    RESPONSE_POWER_OFF_MISS_STATE,
    RESPONSE_POWER_OFF_NO_STATE,
    RESPONSE_POWER_OFF_NONE,
    RESPONSE_POWER_ON_NOT,
    RESPONSE_POWER_ON_OK,
    RESPONSE_POWER_STATE_DOWN,
    RESPONSE_POWER_STATE_EMPTY,
    RESPONSE_POWER_STATE_ON,
    STATE_OFF_RESP,
    STATE_ON_RESP,
)
from tests.test_base import TestBase


class TestPowerOn(TestBase):
    args = ["--power-on"]

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_power_on_ok(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + [STATE_OFF_RESP]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, [200, 204], "OK", True)
        self.set_mock_response(mock_delete, 200, "OK")
        self.boot_seq = BOOT_SEQ_RESPONSE_DIRECTOR
        _, err = self.badfish_call()
        assert err == RESPONSE_POWER_ON_OK

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_power_on_not_ok(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + [STATE_OFF_RESP]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, [200, 409], ["OK", "Conflict"], True)
        self.set_mock_response(mock_delete, 200, "OK")
        self.boot_seq = BOOT_SEQ_RESPONSE_DIRECTOR
        _, err = self.badfish_call()
        assert err == RESPONSE_POWER_ON_NOT


class TestPowerOff(TestBase):
    args = ["--power-off"]

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_power_off_no_state(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + ["{}"]
        self.set_mock_response(mock_get, [200, 200, 200, 200, 200, 400], responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.boot_seq = BOOT_SEQ_RESPONSE_DIRECTOR
        _, err = self.badfish_call()
        assert err == RESPONSE_POWER_OFF_NO_STATE

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_power_off_already(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + [STATE_OFF_RESP]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, [200, 409], ["OK", "Conflict"], True)
        self.set_mock_response(mock_delete, 200, "OK")
        self.boot_seq = BOOT_SEQ_RESPONSE_DIRECTOR
        _, err = self.badfish_call()
        assert err == RESPONSE_POWER_OFF_ALREADY

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_power_miss_state(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + [JOB_OK_RESP]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.boot_seq = BOOT_SEQ_RESPONSE_DIRECTOR
        _, err = self.badfish_call()
        assert err == RESPONSE_POWER_OFF_MISS_STATE

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    @patch("badfish.main.Badfish.get_request")
    def test_power_off_none(self, mock_get_req_call, mock_get, mock_post, mock_delete):
        # The power off operation should return None when getting power state
        mock_get_req_call.side_effect = [None]
        self.set_mock_response(mock_get, 200, INIT_RESP)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        _, err = self.badfish_call()
        assert err == RESPONSE_POWER_OFF_NONE


class TestPowerState(TestBase):
    args = ["--power-state"]

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_power_state(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + [STATE_ON_RESP]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        _, err = self.badfish_call()
        assert err == RESPONSE_POWER_STATE_ON

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_power_state_bad_request(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + ["Bad Request"]
        self.set_mock_response(mock_get, [200, 200, 200, 200, 200, 400], responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        _, err = self.badfish_call()
        assert err == RESPONSE_POWER_STATE_DOWN

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_power_state_empty_data(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + ["{}"]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        _, err = self.badfish_call()
        assert err == RESPONSE_POWER_STATE_EMPTY

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    @patch("badfish.main.Badfish.get_request")
    def test_power_state_none(self, mock_get_req_call, mock_get, mock_post, mock_delete):
        # The power state check should return None (simulating communication failure)
        mock_get_req_call.side_effect = [None]
        # Add extra response for the power state call that should fail (404)
        self.set_mock_response(mock_get, [200, 200, 200, 200, 200, 404], INIT_RESP + [""])
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        _, err = self.badfish_call()
        assert err == "- INFO     - Power state:\n- INFO     -     f01-h01-000-r630.host.io: 'Down'\n"
