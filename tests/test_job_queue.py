from asynctest import patch
from tests.config import (
    INIT_RESP,
    JOB_OK_RESP,
    RESPONSE_LS_JOBS,
    BLANK_RESP,
    RESPONSE_CLEAR_JOBS,
    RESPONSE_LS_JOBS_EMPTY,
    RESPONSE_CLEAR_JOBS_UNSUPPORTED,
    RESPONSE_CLEAR_JOBS_LIST,
)
from tests.test_base import TestBase


class TestJobQueue(TestBase):

    @patch("aiohttp.ClientSession.get")
    def test_ls_jobs(self, mock_get):
        option_arg = "--ls-jobs"
        responses_add = [
            JOB_OK_RESP
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.args = [option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_LS_JOBS

    @patch("aiohttp.ClientSession.get")
    def test_ls_jobs_empty(self, mock_get):
        option_arg = "--ls-jobs"
        responses_add = [
            BLANK_RESP
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.args = [option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_LS_JOBS_EMPTY

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_clear_jobs(self, mock_get, mock_post):
        option_arg = "--clear-jobs"
        responses_add = [
            JOB_OK_RESP,
            BLANK_RESP,
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_post, 200, BLANK_RESP)
        self.set_mock_response(mock_get, 200, responses)
        self.args = [option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_CLEAR_JOBS

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_clear_jobs_unsupported(self, mock_get, mock_post, mock_delete):
        option_arg = "--clear-jobs"
        responses_add = [
            JOB_OK_RESP,
            BLANK_RESP,
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_delete, 200, BLANK_RESP)
        self.set_mock_response(mock_post, 200, BLANK_RESP)
        self.set_mock_response(mock_get, [200, 200, 200, 200, 400, 200], responses)
        self.args = [option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_CLEAR_JOBS_UNSUPPORTED

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_clear_jobs_list(self, mock_get, mock_post, mock_delete):
        option_arg = "--clear-jobs"
        responses_add = [
            JOB_OK_RESP,
            BLANK_RESP,
            BLANK_RESP,
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_delete, [400, 400, 200], [BLANK_RESP, BLANK_RESP, BLANK_RESP])
        self.set_mock_response(mock_post, 200, BLANK_RESP)
        self.set_mock_response(mock_get, [200, 200, 200, 200, 400, 400, 400], responses)
        self.args = [option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_CLEAR_JOBS_LIST

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_clear_jobs_force(self, mock_get, mock_post):
        option_arg = "--clear-jobs"
        force_arg = "--force"
        responses_add = [
            JOB_OK_RESP,
            BLANK_RESP,
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_post, 200, BLANK_RESP)
        self.set_mock_response(mock_get, 200, responses)
        self.args = [option_arg, force_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_CLEAR_JOBS