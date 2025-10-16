from unittest.mock import patch

from tests.config import (
    BIOS_RESPONSE_SRIOV,
    BIOS_SET_OK,
    INIT_RESP,
    JOB_OK_RESP,
    RESET_TYPE_RESP,
    SRIOV_ALREADY,
    SRIOV_STATE,
    STATE_ON_RESP,
)
from tests.test_base import TestBase


class TestSriovModeEnable(TestBase):
    args = ["--enable-sriov"]

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.get")
    def test_enable_sriov_ok(self, mock_get, mock_patch, mock_post, mock_delete):
        get_resp = [
            BIOS_RESPONSE_SRIOV % "Disabled",
            RESET_TYPE_RESP,
            STATE_ON_RESP,
            STATE_ON_RESP,
        ]
        responses = INIT_RESP + get_resp
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_patch, 200, ["OK"])
        self.set_mock_response(mock_post, 200, JOB_OK_RESP)
        self.set_mock_response(mock_delete, 200, "OK")
        _, err = self.badfish_call()
        assert err == BIOS_SET_OK

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.get")
    def test_enable_sriov_already(self, mock_get, mock_patch, mock_post, mock_delete):
        get_resp = [
            BIOS_RESPONSE_SRIOV % "Enabled",
            RESET_TYPE_RESP,
            STATE_ON_RESP,
            STATE_ON_RESP,
        ]
        responses = INIT_RESP + get_resp
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_patch, 200, ["OK"])
        self.set_mock_response(mock_post, 200, JOB_OK_RESP)
        self.set_mock_response(mock_delete, 200, "OK")
        _, err = self.badfish_call()
        assert err == SRIOV_ALREADY


class TestSriovModeDisable(TestBase):
    args = ["--disable-sriov"]

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.get")
    def test_disable_sriov_ok(self, mock_get, mock_patch, mock_post, mock_delete):
        get_resp = [
            BIOS_RESPONSE_SRIOV % "Enabled",
            RESET_TYPE_RESP,
            STATE_ON_RESP,
            STATE_ON_RESP,
        ]
        responses = INIT_RESP + get_resp
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_patch, 200, ["OK"])
        self.set_mock_response(mock_post, 200, JOB_OK_RESP)
        self.set_mock_response(mock_delete, 200, "OK")
        _, err = self.badfish_call()
        assert err == BIOS_SET_OK

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.get")
    def test_disable_sriov_already(self, mock_get, mock_patch, mock_post, mock_delete):
        get_resp = [
            BIOS_RESPONSE_SRIOV % "Disabled",
            RESET_TYPE_RESP,
            STATE_ON_RESP,
            STATE_ON_RESP,
        ]
        responses = INIT_RESP + get_resp
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_patch, 200, ["OK"])
        self.set_mock_response(mock_post, 200, JOB_OK_RESP)
        self.set_mock_response(mock_delete, 200, "OK")
        _, err = self.badfish_call()
        assert err == SRIOV_ALREADY


class TestSriovModeGet(TestBase):
    args = ["--get-sriov"]

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_get_sriov_ok(self, mock_get, mock_post, mock_delete):
        get_resp = [
            BIOS_RESPONSE_SRIOV % "Enabled",
        ]
        responses = INIT_RESP + get_resp
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        _, err = self.badfish_call()
        assert err == SRIOV_STATE
