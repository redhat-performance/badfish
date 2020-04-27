from asynctest import patch
from tests.config import (
    BOOT_SEQ_RESPONSE_DIRECTOR,
    DEVICE_NIC_2,
    RESPONSE_BOOT_TO,
    BAD_DEVICE_NAME,
    ERROR_DEV_NO_MATCH,
    BOOT_SEQ_RESP,
    BOOT_MODE_RESP,
    INIT_RESP,
    BLANK_RESP,
    JOB_OK_RESP,
)
from tests.test_base import TestBase


class TestBootTo(TestBase):
    option_arg = "--boot-to"

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.get")
    def test_boot_to(self, mock_get, mock_patch, mock_post):
        boot_seq_resp_fmt = BOOT_SEQ_RESP % str(BOOT_SEQ_RESPONSE_DIRECTOR)
        get_resp = [
            BOOT_MODE_RESP,
            boot_seq_resp_fmt.replace("'", '"'),
            BLANK_RESP,
        ]
        responses = INIT_RESP + get_resp
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_patch, 200, ["OK"])
        self.set_mock_response(mock_post, 200, JOB_OK_RESP)
        self.args = [self.option_arg, DEVICE_NIC_2["name"]]
        _, err = self.badfish_call()
        assert err == RESPONSE_BOOT_TO

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.get")
    def test_boot_to_no_match(self, mock_get, mock_patch, mock_post):
        boot_seq_resp_fmt = BOOT_SEQ_RESP % str(BOOT_SEQ_RESPONSE_DIRECTOR)
        get_resp = [
            BOOT_MODE_RESP,
            boot_seq_resp_fmt.replace("'", '"'),
            BLANK_RESP,
        ]
        responses = INIT_RESP + get_resp
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_patch, 200, ["OK"])
        self.set_mock_response(mock_post, 200, JOB_OK_RESP)
        self.args = [self.option_arg, BAD_DEVICE_NAME]
        _, err = self.badfish_call()
        assert err == ERROR_DEV_NO_MATCH
