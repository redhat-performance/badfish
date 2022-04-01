from asynctest import patch

import src.badfish.badfish
from tests.config import (
    INIT_RESP,
    STATE_ON_RESP,
    STATE_OFF_RESP,
    RESPONSE_REBOOT_ONLY_SUCCESS,
    BOOT_SEQ_RESPONSE_DIRECTOR,
    RESET_TYPE_RESP,
    STATE_DOWN_RESP,
    RESPONSE_REBOOT_ONLY_FAILED_SEND_RESET,
    RESET_TYPE_NG_RESP,
    RESPONSE_REBOOT_ONLY_SUCCESS_WITH_NG_RT,
    RESPONSE_REBOOT_ONLY_FAILED_GRACE_AND_FORCE,
)
from tests.test_base import TestBase


class TestRebootOnly(TestBase):
    option_arg = "--reboot-only"

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_reboot_only_success(self, mock_get, mock_post):
        responses = INIT_RESP + [
            RESET_TYPE_RESP,
            STATE_ON_RESP,
            STATE_OFF_RESP,
            STATE_ON_RESP,
        ]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 204, ["ok"])
        self.boot_seq = BOOT_SEQ_RESPONSE_DIRECTOR
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_REBOOT_ONLY_SUCCESS

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_reboot_only_success_with_polling_down(self, mock_get, mock_post):
        responses = INIT_RESP + [
            RESET_TYPE_RESP,
            STATE_ON_RESP,
            STATE_DOWN_RESP,
            STATE_ON_RESP,
        ]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 204, ["ok"])
        self.boot_seq = BOOT_SEQ_RESPONSE_DIRECTOR
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_REBOOT_ONLY_SUCCESS

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_reboot_only_success_with_polling_down(self, mock_get, mock_post):
        responses = INIT_RESP + [
            RESET_TYPE_RESP,
            STATE_ON_RESP,
            STATE_DOWN_RESP,
            STATE_ON_RESP,
        ]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 400, ["Bad Request"])
        self.boot_seq = BOOT_SEQ_RESPONSE_DIRECTOR
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_REBOOT_ONLY_FAILED_SEND_RESET

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_reboot_only_success_with_ng_rt(self, mock_get, mock_post):
        responses = INIT_RESP + [
            RESET_TYPE_NG_RESP,
            STATE_ON_RESP,
            STATE_DOWN_RESP,
            STATE_ON_RESP,
        ]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 204, ["ok"])
        self.boot_seq = BOOT_SEQ_RESPONSE_DIRECTOR
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_REBOOT_ONLY_SUCCESS_WITH_NG_RT

    @patch("src.badfish.badfish.RETRIES", 0)
    @patch("aiohttp.ClientSession.get")
    @patch("aiohttp.ClientSession.post")
    def test_reboot_only_failed_grace_and_force(self, mock_post, mock_get):
        responses = INIT_RESP + [
            RESET_TYPE_RESP,
            STATE_ON_RESP,
        ]
        self.set_mock_response(mock_post, 409, ["Conflict"])
        self.set_mock_response(mock_get, 200, responses)
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_REBOOT_ONLY_FAILED_GRACE_AND_FORCE
