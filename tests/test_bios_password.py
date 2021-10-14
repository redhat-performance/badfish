from asynctest import patch
from tests.config import (
    INIT_RESP,
    BLANK_RESP,
    JOB_OK_RESP,
    RESET_TYPE_RESP,
    STATE_ON_RESP,
    BIOS_PASS_SET_GOOD,
    BIOS_PASS_RM_GOOD,
    BIOS_PASS_RM_MISS_ARG,
    BIOS_PASS_SET_MISS_ARG,
)
from tests.test_base import TestBase


class TestSetBiosPass(TestBase):
    option_arg = "--set-bios-password"

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_set_bios_pass_ok(self, mock_get, mock_post):
        responses_get = [
            BLANK_RESP,
            RESET_TYPE_RESP,
            STATE_ON_RESP,
        ]
        responses = INIT_RESP + responses_get
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, JOB_OK_RESP)
        self.args = [self.option_arg, "--new-password", "new_pass"]
        _, err = self.badfish_call()
        assert err == BIOS_PASS_SET_GOOD

    @patch("aiohttp.ClientSession.get")
    def test_set_bios_pass_missing_arg(self, mock_get):
        responses_get = [
            BLANK_RESP,
        ]
        responses = INIT_RESP + responses_get
        self.set_mock_response(mock_get, 200, responses)
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == BIOS_PASS_SET_MISS_ARG


class TestRemoveBiosPass(TestBase):
    option_arg = "--remove-bios-password"

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_rm_bios_pass_ok(self, mock_get, mock_post):
        responses_get = [
            BLANK_RESP,
            RESET_TYPE_RESP,
            STATE_ON_RESP,
        ]
        responses = INIT_RESP + responses_get
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, JOB_OK_RESP)
        self.args = [self.option_arg, "--old-password", "new_pass"]
        _, err = self.badfish_call()
        assert err == BIOS_PASS_RM_GOOD

    @patch("aiohttp.ClientSession.get")
    def test_rm_bios_pass_missing_arg(self, mock_get):
        responses_get = [
            BLANK_RESP,
        ]
        responses = INIT_RESP + responses_get
        self.set_mock_response(mock_get, 200, responses)
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == BIOS_PASS_RM_MISS_ARG
