from unittest.mock import patch

from tests.config import (
    BOOT_MODE_RESP,
    BOOT_SEQ_RESP,
    BOOT_SEQ_RESPONSE_DIRECTOR,
    BOOT_SEQ_RESPONSE_FOREMAN,
    BOOT_SEQ_RESPONSE_NO_MATCH,
    INIT_RESP,
    INTERFACES_PATH,
    RESPONSE_DIRECTOR,
    RESPONSE_FOREMAN,
    RESPONSE_WITHOUT,
    WARN_NO_MATCH,
)
from tests.test_base import TestBase


class TestCheckBoot(TestBase):
    option_arg = "--check-boot"

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_check_boot_without_interfaces(self, mock_get, mock_post, mock_delete):
        boot_seq_resp_fmt = BOOT_SEQ_RESP % str(BOOT_SEQ_RESPONSE_DIRECTOR)
        responses_add = [BOOT_MODE_RESP, boot_seq_resp_fmt.replace("'", '"')]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_WITHOUT

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_check_boot_with_interfaces_director(self, mock_get, mock_post, mock_delete):
        boot_seq_resp_fmt = BOOT_SEQ_RESP % str(BOOT_SEQ_RESPONSE_DIRECTOR)
        responses_add = [BOOT_MODE_RESP, boot_seq_resp_fmt.replace("'", '"')]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = ["-i", INTERFACES_PATH, self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_DIRECTOR

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_check_boot_with_interfaces_foreman(self, mock_get, mock_post, mock_delete):
        boot_seq_resp_fmt = BOOT_SEQ_RESP % str(BOOT_SEQ_RESPONSE_FOREMAN)
        responses_add = [BOOT_MODE_RESP, boot_seq_resp_fmt.replace("'", '"')]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = ["-i", INTERFACES_PATH, self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_FOREMAN

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_check_boot_no_match(self, mock_get, mock_post, mock_delete):
        boot_seq_resp_fmt = BOOT_SEQ_RESP % str(BOOT_SEQ_RESPONSE_NO_MATCH)
        responses_add = [BOOT_MODE_RESP, boot_seq_resp_fmt.replace("'", '"')]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = ["-i", INTERFACES_PATH, self.option_arg]
        _, err = self.badfish_call()
        assert err == WARN_NO_MATCH
