from asynctest import patch
from tests.config import (
    INIT_RESP,
    JOB_OK_RESP,
    VMEDIA_GET_VM_RESP,
    VMEDIA_GET_MEMBERS_RESP,
    VMEDIA_GET_ENDPOINT_FALSE,
    VMEDIA_GET_ENDPOINT_EMPTY,
    VMEDIA_MEMBER_RM_DISK_RESP,
    VMEDIA_MEMBER_CD_RESP,
    VMEDIA_CHECK_GOOD,
    VMEDIA_CHECK_EMPTY,
    VMEDIA_GET_CONF_RESP,
    VMEDIA_UNMOUNT_OK,
    VMEDIA_UNMOUNT_UNSUPPORTED,
    VMEDIA_FIRMWARE_ERROR,
    VMEDIA_CONFIG_NO_MEDIA,
    VMEDIA_UNMOUNT_WENT_WRONG,
    VMEDIA_CHECK_DISC_VALUE_ERROR,
    VMEDIA_NO_ENDPOINT_ERROR,
)
from tests.test_base import TestBase


class TestCheckVirtualMedia(TestBase):
    option_arg = "--check-virtual-media"

    @patch("aiohttp.ClientSession.get")
    def test_check_virtual_media_good(self, mock_get):
        responses_get = [
            VMEDIA_GET_VM_RESP,
            VMEDIA_GET_MEMBERS_RESP,
            VMEDIA_MEMBER_RM_DISK_RESP,
            VMEDIA_MEMBER_CD_RESP,
        ]
        responses = INIT_RESP + responses_get
        self.set_mock_response(mock_get, 200, responses)
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == VMEDIA_CHECK_GOOD

    @patch("aiohttp.ClientSession.get")
    def test_check_virtual_media_empty(self, mock_get):
        responses_get = [
            VMEDIA_GET_VM_RESP,
            "{}",
        ]
        responses = INIT_RESP + responses_get
        self.set_mock_response(mock_get, 200, responses)
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == VMEDIA_CHECK_EMPTY

    @patch("aiohttp.ClientSession.get")
    def test_check_vmedia_disc_value_error(self, mock_get):
        responses_get = [
            VMEDIA_GET_VM_RESP,
            VMEDIA_GET_MEMBERS_RESP,
            ""
        ]
        responses = INIT_RESP + responses_get
        self.set_mock_response(mock_get, 200, responses)
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == VMEDIA_CHECK_DISC_VALUE_ERROR

    @patch("aiohttp.ClientSession.get")
    def test_check_vmedia_get_no_endpoint(self, mock_get):
        responses_get = [
            VMEDIA_GET_ENDPOINT_FALSE
        ]
        responses = INIT_RESP + responses_get
        self.set_mock_response(mock_get, 200, responses)
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == VMEDIA_NO_ENDPOINT_ERROR

    @patch("aiohttp.ClientSession.get")
    def test_check_vmedia_get_endpoint_empty(self, mock_get):
        responses_get = [
            VMEDIA_GET_ENDPOINT_EMPTY
        ]
        responses = INIT_RESP + responses_get
        self.set_mock_response(mock_get, 200, responses)
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == VMEDIA_NO_ENDPOINT_ERROR

    @patch("aiohttp.ClientSession.get")
    def test_check_vmedia_get_empty(self, mock_get):
        responses_get = [
            ""
        ]
        responses = INIT_RESP + responses_get
        self.set_mock_response(mock_get, 200, responses)
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == VMEDIA_FIRMWARE_ERROR

    @patch("aiohttp.ClientSession.get")
    def test_check_vmedia_get_vm_response_empty(self, mock_get):
        responses_get = [
            VMEDIA_GET_VM_RESP,
            ""
        ]
        responses = INIT_RESP + responses_get
        self.set_mock_response(mock_get, 200, responses)
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == VMEDIA_FIRMWARE_ERROR


class TestUnmountVirtualMedia(TestBase):
    option_arg = "--unmount-virtual-media"

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_unmount_virtual_media_ok(self, mock_get, mock_post):
        responses_get = [
            VMEDIA_GET_VM_RESP,
            VMEDIA_GET_CONF_RESP,
        ]
        responses = INIT_RESP + responses_get
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, JOB_OK_RESP)
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == VMEDIA_UNMOUNT_OK

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_unmount_virtual_media_unsupported(self, mock_get, mock_post):
        responses_get = [
            VMEDIA_GET_VM_RESP,
            "{}",
        ]
        responses = INIT_RESP + responses_get
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, JOB_OK_RESP)
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == VMEDIA_UNMOUNT_UNSUPPORTED

    @patch("aiohttp.ClientSession.get")
    def test_unmount_vmedia_config_firmware_error(self, mock_get):
        responses_get = [
            "",
        ]
        responses = INIT_RESP + responses_get
        self.set_mock_response(mock_get, 200, responses)
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == VMEDIA_FIRMWARE_ERROR

    @patch("aiohttp.ClientSession.get")
    def test_unmount_vmedia_config_no_media(self, mock_get):
        responses_get = [
            VMEDIA_GET_VM_RESP,
            ""
        ]
        responses = INIT_RESP + responses_get
        self.set_mock_response(mock_get, 200, responses)
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == VMEDIA_CONFIG_NO_MEDIA

    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_unmount_vmedia_went_wrong(self, mock_get, mock_post):
        responses_get = [
            VMEDIA_GET_VM_RESP,
            VMEDIA_GET_CONF_RESP
        ]
        responses = INIT_RESP + responses_get
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 400, "Bad Request")
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == VMEDIA_UNMOUNT_WENT_WRONG
