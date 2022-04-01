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
    STATE_ON_RESP,
    RESPONSE_POWER_STATE_ON,
    RESPONSE_POWER_STATE_DOWN,
    RESPONSE_POWER_STATE_EMPTY,
    RESPONSE_POWER_OFF_NONE,
)
from tests.test_base import TestBase, MockResponse


class TestPowerOn(TestBase):
    args = ["--power-on"]

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_power_on_ok(self, mock_get, mock_post):
        responses = INIT_RESP + [STATE_OFF_RESP]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 204, ["ok"])
        self.boot_seq = BOOT_SEQ_RESPONSE_DIRECTOR
        _, err = self.badfish_call()
        assert err == RESPONSE_POWER_ON_OK

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_power_on_not_ok(self, mock_get, mock_post):
        responses = INIT_RESP + [STATE_OFF_RESP]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 409, ["ok"])
        self.boot_seq = BOOT_SEQ_RESPONSE_DIRECTOR
        _, err = self.badfish_call()
        assert err == RESPONSE_POWER_ON_NOT


class TestPowerOff(TestBase):
    args = ["--power-off"]

    @patch("aiohttp.ClientSession.get")
    def test_power_off_no_state(self, mock_get):
        responses = INIT_RESP
        self.set_mock_response(mock_get, [200, 200, 200, 200, 400], responses)
        self.boot_seq = BOOT_SEQ_RESPONSE_DIRECTOR
        _, err = self.badfish_call()
        assert err == RESPONSE_POWER_OFF_NO_STATE

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_power_off_already(self, mock_get, mock_post):
        responses = INIT_RESP + [STATE_OFF_RESP]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 409, ["ok"])
        self.boot_seq = BOOT_SEQ_RESPONSE_DIRECTOR
        _, err = self.badfish_call()
        assert err == RESPONSE_POWER_OFF_ALREADY

    @patch("aiohttp.ClientSession.get")
    def test_power_miss_state(self, mock_get):
        responses = INIT_RESP + [JOB_OK_RESP]
        self.set_mock_response(mock_get, 200, responses)
        self.boot_seq = BOOT_SEQ_RESPONSE_DIRECTOR
        _, err = self.badfish_call()
        assert err == RESPONSE_POWER_OFF_MISS_STATE

    @patch("src.badfish.badfish.Badfish.get_request")
    def test_power_off_none(self, mock_get_req_call):
        responses = INIT_RESP
        mock_get_req_call.side_effect = [
            MockResponse(responses[0], 200),
            MockResponse(responses[0], 200),
            MockResponse(responses[1], 200),
            MockResponse(responses[2], 200),
            MockResponse(responses[3], 200),
            None
        ]
        _, err = self.badfish_call()
        assert err == RESPONSE_POWER_OFF_NONE


class TestPowerState(TestBase):
    args = ["--power-state"]

    @patch("aiohttp.ClientSession.get")
    def test_power_state(self, mock_get):
        responses = INIT_RESP + [
            STATE_ON_RESP
        ]
        self.set_mock_response(mock_get, 200, responses)
        _, err = self.badfish_call()
        assert err == RESPONSE_POWER_STATE_ON

    @patch("aiohttp.ClientSession.get")
    def test_power_state_bad_request(self, mock_get):
        responses = INIT_RESP + [
            "Bad Request"
        ]
        self.set_mock_response(mock_get, [200, 200, 200, 200, 400], responses)
        _, err = self.badfish_call()
        assert err == RESPONSE_POWER_STATE_DOWN

    @patch("aiohttp.ClientSession.get")
    def test_power_state_empty_data(self, mock_get):
        responses = INIT_RESP + [
            "{}"
        ]
        self.set_mock_response(mock_get, 200, responses)
        _, err = self.badfish_call()
        assert err == RESPONSE_POWER_STATE_EMPTY

    @patch("src.badfish.badfish.Badfish.get_request")
    def test_power_state_none(self, mock_get_req_call):
        responses = INIT_RESP
        mock_get_req_call.side_effect = [
            MockResponse(responses[0], 200),
            MockResponse(responses[0], 200),
            MockResponse(responses[1], 200),
            MockResponse(responses[2], 200),
            MockResponse(responses[3], 200),
            None
        ]
        _, err = self.badfish_call()
        assert err == RESPONSE_POWER_STATE_DOWN
