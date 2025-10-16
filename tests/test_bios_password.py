from unittest.mock import patch

from tests.config import (
    BIOS_PASS_CHANGE_CMD_FAILED,
    BIOS_PASS_CHANGE_NOT_SUPPORTED,
    BIOS_PASS_RM_GOOD,
    BIOS_PASS_RM_MISS_ARG,
    BIOS_PASS_SET_CHECK_JOB_STATUS_BAD_CODE,
    BIOS_PASS_SET_CHECK_JOB_STATUS_FAIL_MSG,
    BIOS_PASS_SET_GOOD,
    BIOS_PASS_SET_MISS_ARG,
    BLANK_RESP,
    CHECK_JOB_STATUS_FAIL_MSG,
    CHECK_JOB_STATUS_UNEXPECTED_MSG_CONTENT,
    INIT_RESP,
    JOB_OK_RESP,
    RESET_TYPE_RESP,
    STATE_OFF_RESP,
    TASK_OK_RESP,
)
from tests.test_base import TestBase


class TestSetBiosPass(TestBase):
    option_arg = "--set-bios-password"

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_set_bios_pass_ok(self, mock_get, mock_post, mock_delete):
        responses_get = [
            RESET_TYPE_RESP,
            STATE_OFF_RESP,
            TASK_OK_RESP,
        ]
        responses = INIT_RESP + responses_get
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, JOB_OK_RESP)
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg, "--new-password", "new_pass"]
        _, err = self.badfish_call()
        assert err == BIOS_PASS_SET_GOOD

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_set_bios_pass_missing_arg(self, mock_get, mock_post, mock_delete):
        responses_get = [
            BLANK_RESP,
        ]
        responses = INIT_RESP + responses_get
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == BIOS_PASS_SET_MISS_ARG


class TestRemoveBiosPass(TestBase):
    option_arg = "--remove-bios-password"

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_rm_bios_pass_ok(self, mock_get, mock_post, mock_delete):
        responses_get = [
            RESET_TYPE_RESP,
            STATE_OFF_RESP,
            TASK_OK_RESP,
        ]
        responses = INIT_RESP + responses_get
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, JOB_OK_RESP)
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg, "--old-password", "new_pass"]
        _, err = self.badfish_call()
        assert err == BIOS_PASS_RM_GOOD

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_rm_bios_pass_missing_arg(self, mock_get, mock_post, mock_delete):
        responses_get = [
            BLANK_RESP,
        ]
        responses = INIT_RESP + responses_get
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == BIOS_PASS_RM_MISS_ARG


class TestChangeBiosPass(TestBase):
    option_arg = "--set-bios-password"

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_set_bios_pass_not_supported(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, [200, 404], ["OK", "Not Found"], True)
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg, "--new-password", "new_pass"]
        _, err = self.badfish_call()
        assert err == BIOS_PASS_CHANGE_NOT_SUPPORTED

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_set_bios_pass_cmd_failed(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, [200, 400], ["OK", "Bad Request"], True)
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg, "--new-password", "new_pass"]
        _, err = self.badfish_call()
        assert err == BIOS_PASS_CHANGE_CMD_FAILED


class TestSetBiosPassCheckJobStatus(TestBase):
    option_arg = "--set-bios-password"

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_sbp_check_job_bad_code(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + [
            RESET_TYPE_RESP,
            STATE_OFF_RESP,
            "{}",
        ]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, JOB_OK_RESP)
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg, "--new-password", "new_pass"]
        _, err = self.badfish_call()
        assert err == BIOS_PASS_SET_CHECK_JOB_STATUS_BAD_CODE

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_sbp_check_job_fail_msg(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + [
            RESET_TYPE_RESP,
            STATE_OFF_RESP,
            CHECK_JOB_STATUS_FAIL_MSG,
        ]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, JOB_OK_RESP)
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg, "--new-password", "new_pass"]
        _, err = self.badfish_call()
        assert err == BIOS_PASS_SET_CHECK_JOB_STATUS_FAIL_MSG

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_sbp_check_job_unexpected_msg(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + [
            RESET_TYPE_RESP,
            STATE_OFF_RESP,
            CHECK_JOB_STATUS_UNEXPECTED_MSG_CONTENT,
            TASK_OK_RESP,
        ]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, JOB_OK_RESP)
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg, "--new-password", "new_pass"]
        _, err = self.badfish_call()
        assert err == BIOS_PASS_SET_GOOD
