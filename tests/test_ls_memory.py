from asynctest import patch
from tests.config import (
    INIT_RESP,
    MEMORY_MEMBERS_RESP,
    MEMORY_SUMMARY_RESP,
    MEMORY_A5_RESP,
    MEMORY_B2_RESP,
    RESPONSE_LS_MEMORY,
    RESPONSE_LS_MEMORY_SUMMARY_VALUE_ERROR,
    MEMORY_SUMMARY_RESP_FAULTY,
    RESPONSE_LS_MEMORY_SUMMARY_PROC_DATA_ERROR,
    RESPONSE_LS_MEMORY_DETAILS_NOT_FOUND,
    RESPONSE_LS_MEMORY_DETAILS_VALUE_ERROR,
)
from tests.test_base import TestBase


class TestLsMemory(TestBase):
    option_arg = "--ls-memory"

    @patch("aiohttp.ClientSession.get")
    def test_ls_memory(self, mock_get):
        responses_add = [
            MEMORY_SUMMARY_RESP,  # beginning in get_memory_summary()
            MEMORY_MEMBERS_RESP,  # beginning in get_memory_details()
            MEMORY_A5_RESP,       # for cycle first iteration in get_memory_details()
            MEMORY_B2_RESP,       # for cycle second iteration in get_memory_details()
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_LS_MEMORY

    @patch("aiohttp.ClientSession.get")
    def test_ls_memory_summary_value_error(self, mock_get):
        responses_add = [
            ""
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_LS_MEMORY_SUMMARY_VALUE_ERROR

    @patch("aiohttp.ClientSession.get")
    def test_ls_memory_summary_proc_data_error(self, mock_get):
        responses_add = [
            MEMORY_SUMMARY_RESP_FAULTY,
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_LS_MEMORY_SUMMARY_PROC_DATA_ERROR

    @patch("aiohttp.ClientSession.get")
    def test_ls_memory_details_not_found(self, mock_get):
        responses_add = [
            MEMORY_SUMMARY_RESP,  # beginning in get_memory_summary()
            "Not Found",
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, [200, 200, 200, 200, 404], responses)
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_LS_MEMORY_DETAILS_NOT_FOUND

    @patch("aiohttp.ClientSession.get")
    def test_ls_memory_details_value_error(self, mock_get):
        responses_add = [
            MEMORY_SUMMARY_RESP,  # beginning in get_memory_summary()
            "",
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_LS_MEMORY_DETAILS_VALUE_ERROR
