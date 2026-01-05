from unittest.mock import patch

from tests.config import (
    INIT_RESP,
    PROCESSOR_CPU_RESP,
    PROCESSOR_MEMBERS_RESP,
    PROCESSOR_SUMMARY_RESP,
    PROCESSOR_SUMMARY_RESP_FAULTY,
    RESPONSE_LS_PROCESSORS,
    RESPONSE_LS_PROCESSORS_DETAILS_NOT_FOUND,
    RESPONSE_LS_PROCESSORS_DETAILS_VALUE_ERROR,
    RESPONSE_LS_PROCESSORS_SUMMARY_PROC_DATA_ERROR,
    RESPONSE_LS_PROCESSORS_SUMMARY_VALUE_ERROR,
)
from tests.test_base import TestBase


class TestLsProcessors(TestBase):
    option_arg = "--ls-processors"

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_ls_processors(self, mock_get, mock_post, mock_delete):
        responses_add = [
            PROCESSOR_SUMMARY_RESP,
            PROCESSOR_MEMBERS_RESP,
            PROCESSOR_CPU_RESP % ("1", "1"),
            PROCESSOR_CPU_RESP % ("2", "2"),
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_LS_PROCESSORS

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_ls_processors_summary_proc_data_error(self, mock_get, mock_post, mock_delete):
        responses_add = [
            PROCESSOR_SUMMARY_RESP_FAULTY,
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_LS_PROCESSORS_SUMMARY_PROC_DATA_ERROR

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_ls_processors_summary_value_error(self, mock_get, mock_post, mock_delete):
        responses_add = [
            "",
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_LS_PROCESSORS_SUMMARY_VALUE_ERROR

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    @patch("badfish.main.Badfish.get_processor_summary")
    @patch("badfish.main.Badfish.get_processor_details")
    def test_ls_processors_details_not_found(
        self, mock_get_proc_details, mock_get_proc_summary, mock_get, mock_post, mock_delete
    ):
        from badfish.main import BadfishException

        # Mock successful processor summary (the data from PROCESSOR_SUMMARY_RESP)
        processor_summary = {
            "Count": 2,
            "LogicalProcessorCount": 80,
            "Model": "Intel(R) Xeon(R) Gold 6230 CPU @ 2.10GHz",
        }
        mock_get_proc_summary.return_value = processor_summary

        # Mock processor details to raise the expected exception
        mock_get_proc_details.side_effect = BadfishException("Server does not support this functionality")

        self.set_mock_response(mock_get, 200, INIT_RESP)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_LS_PROCESSORS_DETAILS_NOT_FOUND

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_ls_processors_details_value_error(self, mock_get, mock_post, mock_delete):
        responses_add = [PROCESSOR_SUMMARY_RESP, ""]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_LS_PROCESSORS_DETAILS_VALUE_ERROR
