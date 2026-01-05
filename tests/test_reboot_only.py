from unittest.mock import patch

from tests.config import (
    BOOT_SEQ_RESPONSE_DIRECTOR,
    INIT_RESP,
    RESET_TYPE_NG_RESP,
    RESET_TYPE_RESP,
    RESPONSE_REBOOT_ONLY_FAILED_SEND_RESET,
    RESPONSE_REBOOT_ONLY_SUCCESS,
    RESPONSE_REBOOT_ONLY_SUCCESS_WITH_NG_RT,
    STATE_DOWN_RESP,
    STATE_OFF_RESP,
    STATE_ON_RESP,
)
from tests.test_base import TestBase


class TestRebootOnly(TestBase):
    option_arg = "--reboot-only"

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_reboot_only_success(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + [
            RESET_TYPE_RESP,
            STATE_ON_RESP,
            STATE_OFF_RESP,
            STATE_ON_RESP,
        ]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, [200, 204, 204], "OK", True)
        self.set_mock_response(mock_delete, 200, "OK")
        self.boot_seq = BOOT_SEQ_RESPONSE_DIRECTOR
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_REBOOT_ONLY_SUCCESS

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_reboot_only_success_with_polling_down(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + [
            RESET_TYPE_RESP,
            STATE_ON_RESP,
            STATE_DOWN_RESP,
            STATE_ON_RESP,
        ]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, [200, 204, 204], "OK", True)
        self.set_mock_response(mock_delete, 200, "OK")
        self.boot_seq = BOOT_SEQ_RESPONSE_DIRECTOR
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_REBOOT_ONLY_SUCCESS

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_reboot_only_failed_send_reset(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + [
            RESET_TYPE_RESP,
            STATE_ON_RESP,
            STATE_DOWN_RESP,
            STATE_ON_RESP,
        ]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, [200, 400], ["OK", "Bad Request"], True)
        self.set_mock_response(mock_delete, 200, "OK")
        self.boot_seq = BOOT_SEQ_RESPONSE_DIRECTOR
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_REBOOT_ONLY_FAILED_SEND_RESET

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_reboot_only_success_with_ng_rt(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + [
            RESET_TYPE_NG_RESP,
            STATE_ON_RESP,
            STATE_DOWN_RESP,
            STATE_ON_RESP,
        ]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, [200, 204, 204], "OK", True)
        self.set_mock_response(mock_delete, 200, "OK")
        self.boot_seq = BOOT_SEQ_RESPONSE_DIRECTOR
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_REBOOT_ONLY_SUCCESS_WITH_NG_RT

    @patch("badfish.main.RETRIES", 0)
    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.get")
    @patch("aiohttp.ClientSession.post")
    def test_reboot_only_failed_grace_and_force(self, mock_post, mock_get, mock_delete):
        responses = INIT_RESP + [
            RESET_TYPE_RESP,
            STATE_ON_RESP,
        ]
        self.set_mock_response(mock_get, 200, responses)
        # Provide enough POST responses to handle the entire reboot sequence
        self.set_mock_response(mock_post, [200] + [409] * 10, ["OK"] + ["Conflict"] * 10, True)
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        # The test should complete without StopIteration and show reboot failures
        # Checking for key failure indicators rather than exact match
        assert "Command failed to GracefulRestart" in err
        assert "Command failed to ForceOff" in err
