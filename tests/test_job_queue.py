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
    JOB_ID,
    TASK_OK_RESP,
    RESPONSE_CHECK_JOB,
    RESPONSE_CHECK_JOB_BAD,
    RESPONSE_CLEAR_JOBS_LIST_EXCEPTION,
    RESPONSE_CHECK_JOB_ERROR,
    RESPONSE_DELETE_JOBS_UNSUPPORTED_EXCEPTION,
    RESPONSE_DELETE_JOBS_SUPPORTED_EXCEPTION,
)
from tests.test_base import TestBase, MockResponse
from src.badfish.main import BadfishException


def raise_badfish_exception_stub_del_req(arg1=None, arg2=None):
    raise BadfishException


class TestJobQueue(TestBase):
    args = ["--ls-jobs"]

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_ls_jobs(self, mock_get, mock_post, mock_delete):
        responses_add = [JOB_OK_RESP]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        _, err = self.badfish_call()
        assert err == RESPONSE_LS_JOBS

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_ls_jobs_empty(self, mock_get, mock_post, mock_delete):
        responses_add = [BLANK_RESP]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        _, err = self.badfish_call()
        assert err == RESPONSE_LS_JOBS_EMPTY


class TestClearJobs(TestBase):
    args = ["--clear-jobs"]

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_clear_jobs(self, mock_get, mock_post, mock_delete):
        responses_add = [
            JOB_OK_RESP,
            BLANK_RESP,
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        _, err = self.badfish_call()
        assert err == RESPONSE_CLEAR_JOBS

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_clear_jobs_unsupported(self, mock_get, mock_post, mock_delete):
        responses_add = [
            JOB_OK_RESP,
            BLANK_RESP,
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, [200, 200, 200, 200, 200, 400, 200], responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        _, err = self.badfish_call()
        assert err == RESPONSE_CLEAR_JOBS_UNSUPPORTED

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_clear_jobs_list(self, mock_get, mock_post, mock_delete):
        responses_add = [
            JOB_OK_RESP,
            BLANK_RESP,
            BLANK_RESP,
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(
            mock_get, [200, 200, 200, 200, 200, 400, 400, 400], responses
        )
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(
            mock_delete,
            [400, 400, 200, 200],
            ["Bad Request", "Bad Request", "OK", "OK"],
        )
        _, err = self.badfish_call()
        assert err == RESPONSE_CLEAR_JOBS_LIST

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_clear_jobs_force(self, mock_get, mock_post, mock_delete):
        force_arg = "--force"
        responses_add = [
            JOB_OK_RESP,
            BLANK_RESP,
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = self.args + [force_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_CLEAR_JOBS

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_clear_jobs_list_exception(self, mock_get, mock_post, mock_delete):
        responses_add = [
            JOB_OK_RESP,
            BLANK_RESP,
        ]
        responses = INIT_RESP + responses_add
        status_codes = [200, 200, 200, 200, 200, 400, 200]
        self.set_mock_response(mock_get, status_codes, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 400, "Bad Request")
        _, err = self.badfish_call()
        assert err == RESPONSE_CLEAR_JOBS_LIST_EXCEPTION


class TestDeleteJob(TestBase):
    args = ["--clear-jobs"]

    @patch("aiohttp.ClientSession.delete", raise_badfish_exception_stub_del_req)
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_delete_unsupported_exception(self, mock_get, mock_post):
        responses_add = [JOB_OK_RESP]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, [200, 200, 200, 200, 200, 400, 200], responses)
        self.set_mock_response(mock_post, 200, "OK")
        _, err = self.badfish_call()
        assert err == RESPONSE_DELETE_JOBS_UNSUPPORTED_EXCEPTION

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_delete_supported_exception(self, mock_get, mock_post, mock_delete):
        responses_add = [JOB_OK_RESP]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, [200, 400], ["Bad Request", "OK"], True)
        self.set_mock_response(mock_delete, 200, "OK")
        _, err = self.badfish_call()
        assert err == RESPONSE_DELETE_JOBS_SUPPORTED_EXCEPTION


class TestCheckJob(TestBase):
    args = ["--check-job"]

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_check_job_ok(self, mock_get, mock_post, mock_delete):
        responses_add = [
            TASK_OK_RESP,
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = self.args + [JOB_ID]
        _, err = self.badfish_call()
        assert err == RESPONSE_CHECK_JOB

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_check_job_bad(self, mock_get, mock_post, mock_delete):
        responses_add = [
            BLANK_RESP,
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, [200, 200, 200, 200, 200, 404], responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = self.args + ["JID_WHICHDOESNOTEXIST"]
        _, err = self.badfish_call()
        assert err == RESPONSE_CHECK_JOB_BAD

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("src.badfish.main.Badfish.get_request")
    def test_check_job_error(self, mock_get_req_call, mock_post, mock_delete):
        responses = INIT_RESP
        mock_get_req_call.side_effect = [
            MockResponse(responses[0], 200),
            MockResponse(responses[0], 200),
            MockResponse(responses[1], 200),
            MockResponse(responses[2], 200),
            MockResponse(responses[3], 200),
            MockResponse(responses[4], 200),
            None,
        ]
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = self.args + [JOB_ID]
        _, err = self.badfish_call()
        assert err == RESPONSE_CHECK_JOB_ERROR
