import pytest
from asynctest import patch

from src.badfish.main import BadfishException
from tests.config import (
    INIT_RESP,
    GPU_MEMBERS_RESP,
    GPU_MEMBERS_RESP_FAULTY,
    GPU_DATA_RESP1,
    GPU_DATA_RESP2,
    GPU_SUMMARY_RESP,
    RESPONSE_LS_GPU,
    GPU_SUMMARY_RESP_FAULTY,
    RESPONSE_LS_GPU_SUMMARY_DATA_ERROR,
    RESPONSE_LS_GPU_SUMMARY_VALUE_ERROR,
    RESPONSE_LS_GPU_DETAILS_NOT_FOUND,
    RESPONSE_LS_GPU_DETAILS_VALUE_ERROR, RESPONSE_LS_GPU_SUMMARY_BAD_JSON, GPU_DATA_RESP_FAULTY,
)
from tests.test_base import TestBase


class TestLsGpu(TestBase):
    option_arg = "--ls-gpu"

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_ls_gpu(self, mock_get, mock_post, mock_delete):
        responses_add = [
            GPU_MEMBERS_RESP,
            GPU_DATA_RESP1,
            GPU_DATA_RESP2
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_delete,200, "OK")
        self.set_mock_response(mock_post,200, "OK")
        self.set_mock_response(mock_get, 200, responses)
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_LS_GPU

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_ls_gpu_data_not_available(
        self, mock_get, mock_post
    ):
        responses_add = [
            GPU_SUMMARY_RESP_FAULTY,
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_get, [200,200,200,200,200,404], responses)
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_LS_GPU_SUMMARY_DATA_ERROR

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_ls_gpu_summary_data_error(
        self, mock_get, mock_post
    ):
        responses_add = [
            GPU_MEMBERS_RESP,
            GPU_DATA_RESP1,
            GPU_DATA_RESP_FAULTY,
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, [200,200,200,200,200,404,200,200], responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_LS_GPU_SUMMARY_DATA_ERROR

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
