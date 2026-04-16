import os
from datetime import datetime, timedelta
from unittest.mock import patch

from tests.config import (
    BLANK_RESP,
    INIT_RESP,
    JOB_ID,
    RESPONSE_EXPORT_SCP_NO_LOCATION,
    RESPONSE_EXPORT_SCP_PASS,
    RESPONSE_EXPORT_SCP_STATUS_FAIL,
    RESPONSE_EXPORT_SCP_TIME_OUT,
    RESPONSE_GET_SCP_TARGETS_UNSUPPORTED_ERR,
    RESPONSE_GET_SCP_TARGETS_WITH_ALLOWABLES_PASS,
    RESPONSE_GET_SCP_TARGETS_WITHOUT_ALLOWABLES_ERR,
    RESPONSE_GET_SCP_TARGETS_WRONG,
    RESPONSE_IMPORT_SCP_FAIL_STATE,
    RESPONSE_IMPORT_SCP_INVALID_FILEPATH,
    RESPONSE_IMPORT_SCP_PASS,
    RESPONSE_IMPORT_SCP_STATUS_FAIL,
    RESPONSE_IMPORT_SCP_TIME_OUT,
    SCP_GET_TARGETS_ACTIONS_OEM_UNSUPPORTED,
    SCP_GET_TARGETS_ACTIONS_OEM_WITH_ALLOWABLES,
    SCP_GET_TARGETS_ACTIONS_OEM_WITHOUT_ALLOWABLES,
    SCP_MESSAGE_PERCENTAGE,
    SCP_MESSAGE_PERCENTAGE_STATE,
    STATE_ON_RESP,
)
from tests.test_base import TestBase


def fixed_datetime():
    fixed_datetime.counter = getattr(fixed_datetime, "counter", 0) + 1
    if fixed_datetime.counter < 5:
        return datetime.now()
    else:
        return datetime.now() + timedelta(minutes=15)


def export_dir_check():
    if not os.path.exists("exports"):
        os.makedirs("exports")


class TestGetSCPTargets(TestBase):
    option_arg = "--get-scp-targets"

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_with_allowables_pass(self, mock_get, mock_post, mock_delete):
        responses_add = [
            SCP_GET_TARGETS_ACTIONS_OEM_WITH_ALLOWABLES,
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg, "Export"]
        _, err = self.badfish_call()
        assert err == RESPONSE_GET_SCP_TARGETS_WITH_ALLOWABLES_PASS

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_without_allowables_err(self, mock_get, mock_post, mock_delete):
        responses_add = [
            SCP_GET_TARGETS_ACTIONS_OEM_WITHOUT_ALLOWABLES,
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg, "Export"]
        _, err = self.badfish_call()
        assert err == RESPONSE_GET_SCP_TARGETS_WITHOUT_ALLOWABLES_ERR

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_idrac_scp_unsupported_err(self, mock_get, mock_post, mock_delete):
        responses_add = [
            SCP_GET_TARGETS_ACTIONS_OEM_UNSUPPORTED,
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg, "Export"]
        _, err = self.badfish_call()
        assert err == RESPONSE_GET_SCP_TARGETS_UNSUPPORTED_ERR

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_something_wrong(self, mock_get, mock_post, mock_delete):
        responses_add = [
            BLANK_RESP,
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg, "Export"]
        _, err = self.badfish_call()
        assert err == RESPONSE_GET_SCP_TARGETS_WRONG


class TestExportSCP(TestBase):
    option_arg = "--export-scp"

    tests_dir = os.path.dirname(__file__)
    example_path = os.path.join(tests_dir, "fixtures/example_scp.json")

    @patch("badfish.helpers.get_now", fixed_datetime)
    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_pass(self, mock_get, mock_post, mock_delete):
        export_dir_check()
        scp_file = open(self.example_path, "r").read()
        # Provide enough responses for polling loop (up to 50 polls) plus final fetch
        responses_get = [
            SCP_MESSAGE_PERCENTAGE % ("Ex", 15),
            SCP_MESSAGE_PERCENTAGE % ("Ex", 30),
            SCP_MESSAGE_PERCENTAGE % ("Ex", 45),
            SCP_MESSAGE_PERCENTAGE % ("Ex", 60),
            SCP_MESSAGE_PERCENTAGE % ("Ex", 75),
            SCP_MESSAGE_PERCENTAGE % ("Ex", 75),
            SCP_MESSAGE_PERCENTAGE % ("Ex", 90),
            SCP_MESSAGE_PERCENTAGE % ("Ex", 99),
            SCP_MESSAGE_PERCENTAGE_STATE % ("Exporting Server Configuration Profile.", 100, "Completed"),  # Breaks loop
            scp_file,  # Final fetch after loop
        ]
        responses = INIT_RESP + responses_get
        headers = {"Location": f"/{JOB_ID}"}
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, [200, 202], ["OK", "OK"], headers=headers, post=True)
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg, "./exports/"]
        _, err = self.badfish_call()
        assert err == RESPONSE_EXPORT_SCP_PASS % (datetime.now().strftime("%Y-%m-%d_%H%M%S"))

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_status_fail(self, mock_get, mock_post, mock_delete):
        export_dir_check()
        # Provide extra responses in case error_handler makes additional requests
        responses = INIT_RESP + [BLANK_RESP] * 10
        self.set_mock_response(mock_get, 200, responses)
        # export_scp has retry logic that can check status up to 5 times, so provide enough status values
        # First POST is session/auth (200), second POST is export command (400 = fail)
        self.set_mock_response(mock_post, [200, 400, 400, 400, 400, 400], ["OK", "Bad Request", "Bad Request", "Bad Request", "Bad Request", "Bad Request"], post=True)
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg, "./exports/"]
        _, err = self.badfish_call()
        assert err == RESPONSE_EXPORT_SCP_STATUS_FAIL

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_no_location(self, mock_get, mock_post, mock_delete):
        export_dir_check()
        responses = INIT_RESP
        headers = {}
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, [200, 202], ["OK", "OK"], headers=headers, post=True)
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg, "./exports/"]
        _, err = self.badfish_call()
        assert err == RESPONSE_EXPORT_SCP_NO_LOCATION

    @patch("badfish.main.get_now", fixed_datetime)
    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_time_out(self, mock_get, mock_post, mock_delete):
        if hasattr(fixed_datetime, "counter"):
            setattr(fixed_datetime, "counter", 0)
        export_dir_check()
        # New export_scp uses poll count, not time-based timeout
        # Provide responses that never reach 100% completion - poll exhausts at max_polls=50
        # Then final fetch also doesn't have SystemConfiguration
        responses = INIT_RESP + ([SCP_MESSAGE_PERCENTAGE % ("Ex", 1)] * 51) + [BLANK_RESP]
        headers = {"Location": f"/{JOB_ID}"}
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, [200, 202], ["OK", "OK"], headers=headers, post=True)
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg, "./exports/"]
        _, err = self.badfish_call()
        # With new polling logic, job exhausts polls without completion, then fails to find SystemConfiguration
        assert "- INFO     - Job for exporting server configuration" in err
        assert "- INFO     - Exporting Server Configuration Profile., percent complete: 1" in err
        assert "- ERROR    - Export job completed but SystemConfiguration not found in response." in err


class TestImportSCP(TestBase):
    option_arg = "--import-scp"

    tests_dir = os.path.dirname(__file__)
    example_path = os.path.join(tests_dir, "fixtures/example_scp.json")

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_pass(self, mock_get, mock_post, mock_delete):
        export_dir_check()
        responses_get = [
            STATE_ON_RESP,
            SCP_MESSAGE_PERCENTAGE % ("Im", 15),
            SCP_MESSAGE_PERCENTAGE % ("Im", 30),
            SCP_MESSAGE_PERCENTAGE % ("Im", 45),
            SCP_MESSAGE_PERCENTAGE % ("Im", 60),
            SCP_MESSAGE_PERCENTAGE % ("Im", 75),
            SCP_MESSAGE_PERCENTAGE % ("Im", 90),
            SCP_MESSAGE_PERCENTAGE % ("Im", 99),
            SCP_MESSAGE_PERCENTAGE_STATE
            % ("Successfully imported and applied Server Configuration Profile.", 100, "Completed"),
        ]
        responses = INIT_RESP + responses_get
        headers = {"Location": f"/{JOB_ID}"}
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, [200, 202], ["OK", "OK"], headers=headers, post=True)
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg, self.example_path]
        _, err = self.badfish_call()
        assert err == RESPONSE_IMPORT_SCP_PASS

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_invalid_filepath(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg, "no_file"]
        _, err = self.badfish_call()
        assert err == RESPONSE_IMPORT_SCP_INVALID_FILEPATH

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_status_fail(self, mock_get, mock_post, mock_delete):
        responses_get = [STATE_ON_RESP]
        responses = INIT_RESP + responses_get
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, [200, 400], ["OK", "Bad Request"], True)
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg, self.example_path]
        _, err = self.badfish_call()
        assert err == RESPONSE_IMPORT_SCP_STATUS_FAIL

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_no_location(self, mock_get, mock_post, mock_delete):
        export_dir_check()
        responses_get = [STATE_ON_RESP]
        responses = INIT_RESP + responses_get
        headers = {}
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, [200, 202], ["OK", "OK"], headers=headers, post=True)
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg, self.example_path]
        _, err = self.badfish_call()
        assert err == RESPONSE_EXPORT_SCP_NO_LOCATION

    @patch("badfish.main.get_now", fixed_datetime)
    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_time_out(self, mock_get, mock_post, mock_delete):
        if hasattr(fixed_datetime, "counter"):
            setattr(fixed_datetime, "counter", 0)
        export_dir_check()
        responses_get = [
            STATE_ON_RESP,
            "{}",
            INIT_RESP[0],
        ] + ([SCP_MESSAGE_PERCENTAGE % ("Im", 1)] * 1000000)
        responses = INIT_RESP + responses_get
        headers = {"Location": f"/{JOB_ID}"}
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, [200, 202], ["OK", "OK"], headers=headers, post=True)
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg, self.example_path]
        _, err = self.badfish_call()
        assert err == RESPONSE_IMPORT_SCP_TIME_OUT

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_fail_state(self, mock_get, mock_post, mock_delete):
        export_dir_check()
        responses_get = [
            STATE_ON_RESP,
            SCP_MESSAGE_PERCENTAGE % ("Im", 20),
            SCP_MESSAGE_PERCENTAGE % ("Im", 40),
            SCP_MESSAGE_PERCENTAGE % ("Im", 60),
            SCP_MESSAGE_PERCENTAGE_STATE % ("Unable to complete the Import operation.", 100, "Failed"),
        ]
        responses = INIT_RESP + responses_get
        headers = {"Location": f"/{JOB_ID}"}
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, [200, 202], ["OK", "OK"], headers=headers, post=True)
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg, self.example_path]
        _, err = self.badfish_call()
        assert err == RESPONSE_IMPORT_SCP_FAIL_STATE
