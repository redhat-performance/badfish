from asynctest import patch
from tests.config import (
    BOOT_SEQ_RESPONSE_DIRECTOR,
    INTERFACES_PATH,
    RESPONSE_CHANGE_BOOT,
    BOOT_SEQ_RESP,
    BOOT_MODE_RESP,
    INIT_RESP,
    BLANK_RESP,
    STATE_ON_RESP,
    JOB_OK_RESP,
    BOOT_SEQ_RESPONSE_FOREMAN,
    RESPONSE_CHANGE_TO_SAME,
    RESPONSE_CHANGE_BAD_TYPE,
    RESPONSE_CHANGE_NO_INT,
    RESET_TYPE_RESP,
)
from tests.test_base import TestBase


class TestChangeBoot(TestBase):
    option_arg = "-t"

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.get")
    def test_change_to_foreman(self, mock_get, mock_patch, mock_post):
        boot_seq_resp_fmt = BOOT_SEQ_RESP % str(BOOT_SEQ_RESPONSE_DIRECTOR)
        get_resp = [
            BOOT_MODE_RESP,
            boot_seq_resp_fmt.replace("'", '"'),
            BLANK_RESP,
            BOOT_MODE_RESP,
            RESET_TYPE_RESP,
            STATE_ON_RESP,
            STATE_ON_RESP,
        ]
        responses = INIT_RESP + get_resp
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_patch, 200, ["OK"])
        self.set_mock_response(mock_post, 200, JOB_OK_RESP)
        self.args = ["-i", INTERFACES_PATH, self.option_arg, "foreman"]
        _, err = self.badfish_call()
        assert err == RESPONSE_CHANGE_BOOT

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.get")
    def test_change_to_director(self, mock_get, mock_patch, mock_post):
        boot_seq_resp_fmt = BOOT_SEQ_RESP % str(BOOT_SEQ_RESPONSE_FOREMAN)
        get_resp = [
            BOOT_MODE_RESP,
            boot_seq_resp_fmt.replace("'", '"'),
            BLANK_RESP,
            BOOT_MODE_RESP,
            RESET_TYPE_RESP,
            STATE_ON_RESP,
            STATE_ON_RESP,
        ]
        responses = INIT_RESP + get_resp
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_patch, 200, ["OK"])
        self.set_mock_response(mock_post, 200, JOB_OK_RESP)
        self.args = ["-i", INTERFACES_PATH, self.option_arg, "director"]
        _, err = self.badfish_call()
        assert err == RESPONSE_CHANGE_BOOT

    @patch("aiohttp.ClientSession.get")
    def test_change_bad_type(self, mock_get):
        boot_seq_resp_fmt = BOOT_SEQ_RESP % str(BOOT_SEQ_RESPONSE_FOREMAN)
        get_resp = [
            BOOT_MODE_RESP,
            boot_seq_resp_fmt.replace("'", '"'),
            BLANK_RESP,
            STATE_ON_RESP,
            BOOT_MODE_RESP,
            STATE_ON_RESP,
            STATE_ON_RESP,
        ]
        responses = INIT_RESP + get_resp
        self.set_mock_response(mock_get, 200, responses)
        self.args = ["-i", INTERFACES_PATH, self.option_arg, "bad_type"]
        _, err = self.badfish_call()
        assert err == RESPONSE_CHANGE_BAD_TYPE

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.get")
    def test_change_to_same(self, mock_get, mock_patch, mock_post):
        boot_seq_resp_fmt = BOOT_SEQ_RESP % str(BOOT_SEQ_RESPONSE_DIRECTOR)
        get_resp = [
            BOOT_MODE_RESP,
            boot_seq_resp_fmt.replace("'", '"'),
            BLANK_RESP,
            STATE_ON_RESP,
            BOOT_MODE_RESP,
            STATE_ON_RESP,
            STATE_ON_RESP,
        ]
        responses = INIT_RESP + get_resp
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_patch, 200, ["OK"])
        self.set_mock_response(mock_post, 200, JOB_OK_RESP)
        self.args = ["-i", INTERFACES_PATH, self.option_arg, "director"]
        _, err = self.badfish_call()
        assert err == RESPONSE_CHANGE_TO_SAME

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.get")
    def test_change_no_interfaces(self, mock_get, mock_patch, mock_post):
        boot_seq_resp_fmt = BOOT_SEQ_RESP % str(BOOT_SEQ_RESPONSE_FOREMAN)
        get_resp = [
            BOOT_MODE_RESP,
            boot_seq_resp_fmt.replace("'", '"'),
            BLANK_RESP,
            STATE_ON_RESP,
            BOOT_MODE_RESP,
            STATE_ON_RESP,
            STATE_ON_RESP,
        ]
        responses = INIT_RESP + get_resp
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_patch, 200, ["OK"])
        self.set_mock_response(mock_post, 200, JOB_OK_RESP)
        self.args = [self.option_arg, "director"]
        _, err = self.badfish_call()
        assert err == RESPONSE_CHANGE_NO_INT
