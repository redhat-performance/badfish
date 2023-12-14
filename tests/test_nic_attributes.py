from asynctest import patch
from tests.config import (
    INIT_RESP,
    INIT_RESP_SUPERMICRO,
    GET_NIC_FQQDS_ADAPTERS,
    GET_NIC_FQQDS_EMBEDDED,
    GET_NIC_FQQDS_INTEGRATED,
    GET_NIC_FQQDS_SLOT,
    RESPONSE_GET_NIC_FQQDS_OK,
    RESPONSE_GET_NIC_FQQDS_UNSUPPORTED,
    RESPONSE_GET_NIC_FQQDS_INVALID,
    GET_NIC_ATTR_LIST,
    RESPONSE_GET_NIC_ATTR_LIST_OK,
    RESPONSE_GET_NIC_ATTR_LIST_UNSUPPORTED,
    RESPONSE_GET_NIC_ATTR_LIST_INVALID,
    GET_FW_VERSION,
    GET_FW_VERSION_UNSUPPORTED,
    GET_NIC_ATTR_REGISTRY,
    RESPONSE_GET_NIC_ATTR_SPECIFIC,
    RESPONSE_GET_NIC_ATTR_SPECIFIC_VERSION_UNSUPPORTED,
    RESPONSE_GET_NIC_ATTR_SPECIFIC_REGISTRY_FAIL,
    RESPONSE_GET_NIC_ATTR_SPECIFIC_LIST_FAIL,
)
from tests.test_base import TestBase


class TestNICFQDDs(TestBase):
    option_arg = "--get-nic-fqdds"

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_get_nic_fqdds_ok(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + [
            GET_NIC_FQQDS_ADAPTERS,
            GET_NIC_FQQDS_EMBEDDED,
            GET_NIC_FQQDS_INTEGRATED,
            GET_NIC_FQQDS_SLOT,
        ]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [
            self.option_arg,
        ]
        _, err = self.badfish_call()
        assert err == RESPONSE_GET_NIC_FQQDS_OK

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_get_nic_fqdds_unsupported(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + ["{}"]
        self.set_mock_response(mock_get, [200, 200, 200, 200, 200, 404], responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [
            self.option_arg,
        ]
        _, err = self.badfish_call()
        assert err == RESPONSE_GET_NIC_FQQDS_UNSUPPORTED

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_get_nic_fqdds_unsupported(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + ["{}"]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [
            self.option_arg,
        ]
        _, err = self.badfish_call()
        assert err == RESPONSE_GET_NIC_FQQDS_INVALID


class TestGetNICAttribute(TestBase):
    option_arg = "--get-nic-attribute"

    # LIST ALL ATTRIBUTES FOR A NIC
    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_get_nic_attr_list_ok(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + [
            GET_NIC_ATTR_LIST,
        ]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [
            self.option_arg,
            "NIC.Embedded.1-1-1",
        ]
        _, err = self.badfish_call()
        assert err == RESPONSE_GET_NIC_ATTR_LIST_OK

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_get_nic_attr_list_unsupported(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + ["{}"]
        self.set_mock_response(mock_get, [200, 200, 200, 200, 200, 404], responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [
            self.option_arg,
            "NIC.Embedded.1-1-1",
        ]
        _, err = self.badfish_call()
        assert err == RESPONSE_GET_NIC_ATTR_LIST_UNSUPPORTED

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_get_nic_attr_list_invalid(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + ["{}"]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [
            self.option_arg,
            "NIC.Embedded.1-1-1",
        ]
        _, err = self.badfish_call()
        assert err == RESPONSE_GET_NIC_ATTR_LIST_INVALID

    # LIST INFO ABOUT A SPECIFIC ATTRIBUTE
    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_get_nic_attr_info_ok(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + [
            GET_FW_VERSION,
            GET_NIC_ATTR_REGISTRY,
            GET_NIC_ATTR_LIST
        ]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [
            self.option_arg,
            "NIC.Embedded.1-1-1",
            "--attribute",
            "WakeOnLan"
        ]
        _, err = self.badfish_call()
        assert err == RESPONSE_GET_NIC_ATTR_SPECIFIC

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_get_nic_attr_info_vendor_unsupported(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP_SUPERMICRO + [
            GET_FW_VERSION,
        ]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [
            self.option_arg,
            "NIC.Embedded.1-1-1",
            "--attribute",
            "WakeOnLan"
        ]
        _, err = self.badfish_call()
        assert err == RESPONSE_GET_NIC_FQQDS_UNSUPPORTED

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_get_nic_attr_info_version_unsupported(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + [
            GET_FW_VERSION_UNSUPPORTED,
        ]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [
            self.option_arg,
            "NIC.Embedded.1-1-1",
            "--attribute",
            "WakeOnLan"
        ]
        _, err = self.badfish_call()
        assert err == RESPONSE_GET_NIC_ATTR_SPECIFIC_VERSION_UNSUPPORTED

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_get_nic_attr_info_registry_fail(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + [
            GET_FW_VERSION,
            "{}"
        ]
        self.set_mock_response(mock_get, [200, 200, 200, 200, 200, 200, 404], responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [
            self.option_arg,
            "NIC.Embedded.1-1-1",
            "--attribute",
            "WakeOnLan"
        ]
        _, err = self.badfish_call()
        assert err == RESPONSE_GET_NIC_ATTR_SPECIFIC_REGISTRY_FAIL

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_get_nic_attr_info_registry_empty(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + [
            GET_FW_VERSION,
            "{}"
        ]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [
            self.option_arg,
            "NIC.Embedded.1-1-1",
            "--attribute",
            "WakeOnLan"
        ]
        _, err = self.badfish_call()
        assert err == RESPONSE_GET_NIC_ATTR_SPECIFIC_REGISTRY_FAIL

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_get_nic_attr_info_list_empty(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + [
            GET_FW_VERSION,
            GET_NIC_ATTR_REGISTRY,
            "{}",
        ]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [
            self.option_arg,
            "NIC.Embedded.1-1-1",
            "--attribute",
            "WakeOnLan"
        ]
        _, err = self.badfish_call()
        assert err == RESPONSE_GET_NIC_ATTR_SPECIFIC_LIST_FAIL


class TestSetNICAttribute(TestBase):
    option_arg = "--set-nic-attribute"
    # TODO: Fix after iDRAC version update.

    pass
