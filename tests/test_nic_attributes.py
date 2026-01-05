from unittest.mock import patch

from tests.config import (
    GET_FW_VERSION,
    GET_FW_VERSION_UNSUPPORTED,
    GET_NIC_ATTR_LIST,
    GET_NIC_ATTR_REGISTRY,
    GET_NIC_FQQDS_ADAPTERS,
    GET_NIC_FQQDS_EMBEDDED,
    GET_NIC_FQQDS_INTEGRATED,
    GET_NIC_FQQDS_SLOT,
    INIT_RESP,
    INIT_RESP_SUPERMICRO,
    RESET_TYPE_RESP,
    RESPONSE_GET_NIC_ATTR_FW_BAD,
    RESPONSE_GET_NIC_ATTR_LIST_INVALID,
    RESPONSE_GET_NIC_ATTR_LIST_OK,
    RESPONSE_GET_NIC_ATTR_SPECIFIC,
    RESPONSE_GET_NIC_ATTR_SPECIFIC_LIST_FAIL,
    RESPONSE_GET_NIC_ATTR_SPECIFIC_REGISTRY_FAIL,
    RESPONSE_GET_NIC_ATTR_SPECIFIC_VERSION_UNSUPPORTED,
    RESPONSE_GET_NIC_FQQDS_INVALID,
    RESPONSE_GET_NIC_FQQDS_OK,
    RESPONSE_SET_NIC_ATTR_ALREADY_OK,
    RESPONSE_SET_NIC_ATTR_BAD_VALUE,
    RESPONSE_SET_NIC_ATTR_INT_MAXED,
    RESPONSE_SET_NIC_ATTR_OK,
    RESPONSE_SET_NIC_ATTR_RETRY_NOT_OK,
    RESPONSE_SET_NIC_ATTR_RETRY_OK,
    RESPONSE_SET_NIC_ATTR_STR_MAXED,
    RESPONSE_VENDOR_UNSUPPORTED,
    STATE_OFF_RESP,
    STATE_ON_RESP,
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
    def test_get_nic_fqdds_supermicro(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP_SUPERMICRO
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [
            self.option_arg,
        ]
        _, err = self.badfish_call()
        assert err == f"{RESPONSE_VENDOR_UNSUPPORTED}\n"

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_get_nic_fqdds_unsupported(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + ["{}", "{}", "{}"]
        self.set_mock_response(mock_get, 404, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [
            self.option_arg,
        ]
        _, err = self.badfish_call()
        assert err == RESPONSE_VENDOR_UNSUPPORTED + '\n'

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_get_nic_fqdds_invalid(self, mock_get, mock_post, mock_delete):
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
    @patch("badfish.main.Badfish.get_nic_attribute")
    def test_get_nic_attr_list_unsupported(self, mock_get_nic_attr, mock_get, mock_post, mock_delete):
        from badfish.main import BadfishException

        # Mock get_nic_attribute to raise BadfishException with vendor unsupported message
        mock_get_nic_attr.side_effect = BadfishException("Operation not supported by vendor.")

        self.set_mock_response(mock_get, 200, INIT_RESP)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [
            self.option_arg,
            "NIC.Embedded.1-1-1",
        ]
        _, err = self.badfish_call()
        assert err == f"{RESPONSE_VENDOR_UNSUPPORTED}\n"

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
        responses = INIT_RESP + [GET_FW_VERSION, GET_NIC_ATTR_REGISTRY, GET_NIC_ATTR_LIST]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg, "NIC.Embedded.1-1-1", "--attribute", "WakeOnLan"]
        _, err = self.badfish_call()
        assert err == RESPONSE_GET_NIC_ATTR_SPECIFIC

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    @patch("badfish.main.Badfish.get_idrac_fw_version")
    def test_get_nic_attr_fw_bad(self, mock_get_fw, mock_get, mock_post, mock_delete):

        async def fake_get_fw():
            # Emit via Badfish logger name to match formatting
            from logging import getLogger

            getLogger("badfish.helpers.logger").error("Operation not supported by vendor.")
            return 0

        mock_get_fw.side_effect = fake_get_fw

        self.set_mock_response(mock_get, 200, INIT_RESP)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg, "NIC.Embedded.1-1-1", "--attribute", "WakeOnLan"]
        _, err = self.badfish_call()
        assert err == RESPONSE_GET_NIC_ATTR_FW_BAD

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
        self.args = [self.option_arg, "NIC.Embedded.1-1-1", "--attribute", "WakeOnLan"]
        _, err = self.badfish_call()
        assert err == f"{RESPONSE_VENDOR_UNSUPPORTED}\n"

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
        self.args = [self.option_arg, "NIC.Embedded.1-1-1", "--attribute", "WakeOnLan"]
        _, err = self.badfish_call()
        assert err == RESPONSE_GET_NIC_ATTR_SPECIFIC_VERSION_UNSUPPORTED

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_get_nic_attr_info_registry_fail(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + [GET_FW_VERSION, "{}"]
        self.set_mock_response(mock_get, [200, 200, 200, 200, 200, 200, 404], responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg, "NIC.Embedded.1-1-1", "--attribute", "WakeOnLan"]
        _, err = self.badfish_call()
        assert err == RESPONSE_GET_NIC_ATTR_SPECIFIC_REGISTRY_FAIL

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_get_nic_attr_info_registry_empty(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + [GET_FW_VERSION, "{}"]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg, "NIC.Embedded.1-1-1", "--attribute", "WakeOnLan"]
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
        self.args = [self.option_arg, "NIC.Embedded.1-1-1", "--attribute", "WakeOnLan"]
        _, err = self.badfish_call()
        assert err == RESPONSE_GET_NIC_ATTR_SPECIFIC_LIST_FAIL


class TestSetNICAttribute(TestBase):
    option_arg = "--set-nic-attribute"

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_set_nic_attr_already_ok(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + [
            GET_FW_VERSION,
            GET_NIC_ATTR_REGISTRY,
            GET_NIC_ATTR_LIST,
        ]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [
            self.option_arg,
            "NIC.Embedded.1-1-1",
            "--attribute",
            "WakeOnLan",
            "--value",
            "Enabled",
        ]
        _, err = self.badfish_call()
        assert err == RESPONSE_SET_NIC_ATTR_ALREADY_OK

    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_set_nic_attr_ok(self, mock_get, mock_post, mock_delete, mock_patch):
        responses = INIT_RESP + [
            GET_FW_VERSION,
            GET_NIC_ATTR_REGISTRY,
            GET_NIC_ATTR_LIST,
            RESET_TYPE_RESP,
            STATE_OFF_RESP,
        ]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.set_mock_response(mock_patch, 200, "OK")
        self.args = [
            self.option_arg,
            "NIC.Embedded.1-1-1",
            "--attribute",
            "WakeOnLan",
            "--value",
            "Disabled",
        ]
        _, err = self.badfish_call()
        assert err == RESPONSE_SET_NIC_ATTR_OK

    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_set_nic_attr_retry_ok(self, mock_get, mock_post, mock_delete, mock_patch):
        responses = INIT_RESP + [
            GET_FW_VERSION,
            GET_NIC_ATTR_REGISTRY,
            GET_NIC_ATTR_LIST,
            RESET_TYPE_RESP,
            STATE_OFF_RESP,
        ]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.set_mock_response(mock_patch, [503, 200], "OK")
        self.args = [
            self.option_arg,
            "NIC.Embedded.1-1-1",
            "--attribute",
            "WakeOnLan",
            "--value",
            "Disabled",
        ]
        _, err = self.badfish_call()
        assert err == RESPONSE_SET_NIC_ATTR_RETRY_OK

    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_set_nic_attr_retry_not_ok(self, mock_get, mock_post, mock_delete, mock_patch):
        responses = INIT_RESP + [
            GET_FW_VERSION,
            GET_NIC_ATTR_REGISTRY,
            GET_NIC_ATTR_LIST,
            RESET_TYPE_RESP,
            RESET_TYPE_RESP,
            STATE_OFF_RESP,
            STATE_ON_RESP,
            STATE_OFF_RESP,
        ]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.set_mock_response(mock_patch, [400, 200, 200], "OK")
        self.args = [
            self.option_arg,
            "NIC.Embedded.1-1-1",
            "--attribute",
            "WakeOnLan",
            "--value",
            "Disabled",
        ]
        _, err = self.badfish_call()
        assert err == RESPONSE_SET_NIC_ATTR_RETRY_NOT_OK

    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_set_nic_attr_str_ok(self, mock_get, mock_post, mock_delete, mock_patch):
        responses = INIT_RESP + [
            GET_FW_VERSION,
            GET_NIC_ATTR_REGISTRY,
            GET_NIC_ATTR_LIST,
            RESET_TYPE_RESP,
            STATE_OFF_RESP,
        ]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.set_mock_response(mock_patch, 200, "OK")
        self.args = [
            self.option_arg,
            "NIC.Embedded.1-1-1",
            "--attribute",
            "ChipMdl",
            "--value",
            "512",
        ]
        _, err = self.badfish_call()
        assert err == RESPONSE_SET_NIC_ATTR_OK

    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_set_nic_attr_str_maxed(self, mock_get, mock_post, mock_delete, mock_patch):
        responses = INIT_RESP + [
            GET_FW_VERSION,
            GET_NIC_ATTR_REGISTRY,
            GET_NIC_ATTR_LIST,
            RESET_TYPE_RESP,
            STATE_OFF_RESP,
        ]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.set_mock_response(mock_patch, 200, "OK")
        self.args = [
            self.option_arg,
            "NIC.Embedded.1-1-1",
            "--attribute",
            "ChipMdl",
            "--value",
            "a" * 1025,
        ]
        _, err = self.badfish_call()
        assert err == RESPONSE_SET_NIC_ATTR_STR_MAXED

    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_set_nic_attr_int_ok(self, mock_get, mock_post, mock_delete, mock_patch):
        responses = INIT_RESP + [
            GET_FW_VERSION,
            GET_NIC_ATTR_REGISTRY,
            GET_NIC_ATTR_LIST,
            RESET_TYPE_RESP,
            STATE_OFF_RESP,
        ]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.set_mock_response(mock_patch, 200, "OK")
        self.args = [
            self.option_arg,
            "NIC.Embedded.1-1-1",
            "--attribute",
            "BlnkLeds",
            "--value",
            "12",
        ]
        _, err = self.badfish_call()
        assert err == RESPONSE_SET_NIC_ATTR_OK

    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_set_nic_attr_int_maxed(self, mock_get, mock_post, mock_delete, mock_patch):
        responses = INIT_RESP + [
            GET_FW_VERSION,
            GET_NIC_ATTR_REGISTRY,
            GET_NIC_ATTR_LIST,
            RESET_TYPE_RESP,
            STATE_OFF_RESP,
        ]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.set_mock_response(mock_patch, 200, "OK")
        self.args = [
            self.option_arg,
            "NIC.Embedded.1-1-1",
            "--attribute",
            "BlnkLeds",
            "--value",
            "30",
        ]
        _, err = self.badfish_call()
        assert err == RESPONSE_SET_NIC_ATTR_INT_MAXED

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_set_nic_attr_bad_value(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP + [
            GET_FW_VERSION,
            GET_NIC_ATTR_REGISTRY,
            GET_NIC_ATTR_LIST,
        ]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [
            self.option_arg,
            "NIC.Embedded.1-1-1",
            "--attribute",
            "WakeOnLan",
            "--value",
            "BadValue",
        ]
        _, err = self.badfish_call()
        assert err == RESPONSE_SET_NIC_ATTR_BAD_VALUE

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_set_nic_attr_supermicro(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP_SUPERMICRO
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, responses)
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [
            self.option_arg,
            "NIC.Embedded.1-1-1",
            "--attribute",
            "WakeOnLan",
            "--value",
            "Enabled",
        ]
        _, err = self.badfish_call()
        assert err == f"{RESPONSE_VENDOR_UNSUPPORTED}\n"
