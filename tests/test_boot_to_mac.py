from asynctest import patch
from tests.config import (
    BOOT_SEQ_RESPONSE_DIRECTOR,
    RESPONSE_BOOT_TO,
    BOOT_SEQ_RESP,
    BOOT_MODE_RESP,
    INIT_RESP,
    BLANK_RESP,
    JOB_OK_RESP,
    INTERFACES_PATH,
    ETHERNET_INTERFACES_RESP,
    INTERFACES_RESP,
    MAC_ADDRESS,
    RESPONSE_BOOT_TO_BAD_MAC,
)
from tests.test_base import TestBase


class TestBootToMac(TestBase):
    option_arg = "--boot-to-mac"

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.get")
    def test_boot_to_good_mac(self, mock_get, mock_patch, mock_post):
        boot_seq_resp_fmt = BOOT_SEQ_RESP % str(BOOT_SEQ_RESPONSE_DIRECTOR)
        get_resp = [
            ETHERNET_INTERFACES_RESP,
            INTERFACES_RESP,
            BOOT_MODE_RESP,
            boot_seq_resp_fmt.replace("'", '"'),
            BLANK_RESP,
            BOOT_MODE_RESP,
        ]
        responses = INIT_RESP + get_resp
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_patch, 200, ["OK"])
        self.set_mock_response(mock_post, 200, JOB_OK_RESP)
        self.args = ["-i", INTERFACES_PATH, self.option_arg, MAC_ADDRESS]
        _, err = self.badfish_call()
        assert err == RESPONSE_BOOT_TO

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.get")
    def test_boot_to_bad_mac(self, mock_get, mock_patch, mock_post):
        boot_seq_resp_fmt = BOOT_SEQ_RESP % str(BOOT_SEQ_RESPONSE_DIRECTOR)
        get_resp = [
            ETHERNET_INTERFACES_RESP,
            INTERFACES_RESP,
            BOOT_MODE_RESP,
            boot_seq_resp_fmt.replace("'", '"'),
            BLANK_RESP,
            BOOT_MODE_RESP,
        ]
        responses = INIT_RESP + get_resp
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_patch, 200, ["OK"])
        self.set_mock_response(mock_post, 200, JOB_OK_RESP)
        self.args = ["-i", INTERFACES_PATH, self.option_arg, "no:tg:oo:dm:ac"]
        _, err = self.badfish_call()
        assert err == RESPONSE_BOOT_TO_BAD_MAC
