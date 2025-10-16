from unittest.mock import patch

from tests.config import (
    GPU_DATA_RESP1,
    GPU_DATA_RESP2,
    GPU_DATA_RESP_FAULTY,
    GPU_MEMBERS_RESP,
    GPU_SUMMARY_RESP_FAULTY,
    INIT_RESP,
    MOCK_HOST,
    RESPONSE_LS_GPU,
    RESPONSE_LS_GPU_SUMMARY_DATA_ERROR,
    RESPONSE_LS_GPU_SUMMARY_VALUE_ERROR,
)
from tests.test_base import TestBase


class TestLsGpu(TestBase):
    option_arg = "--ls-gpu"

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_ls_gpu(self, mock_get, mock_post, mock_delete):
        responses_add = [GPU_MEMBERS_RESP, GPU_DATA_RESP1, GPU_DATA_RESP2]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_delete, 200, "OK")
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_get, 200, responses)
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_LS_GPU

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_ls_gpu_data_not_available(self, mock_get, mock_post):
        responses_add = [
            GPU_SUMMARY_RESP_FAULTY,
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_get, [200, 200, 200, 200, 200, 404], responses)
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_LS_GPU_SUMMARY_DATA_ERROR

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_ls_gpu_summary_data_error(self, mock_get, mock_post):
        responses_add = [
            GPU_MEMBERS_RESP,
            GPU_DATA_RESP1,
            GPU_DATA_RESP_FAULTY,
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, [200, 200, 200, 200, 200, 404, 200, 200], responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert (
            err
            == RESPONSE_LS_GPU_SUMMARY_VALUE_ERROR
            + f"- WARNING  - Failed to delete session for {MOCK_HOST}: Failed to communicate with server.\n"
        )

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_ls_gpu_summary_value_error(self, mock_get, mock_post, mock_delete):
        responses_add = [
            GPU_MEMBERS_RESP,
            GPU_DATA_RESP1,
            GPU_DATA_RESP_FAULTY,
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_LS_GPU_SUMMARY_VALUE_ERROR
