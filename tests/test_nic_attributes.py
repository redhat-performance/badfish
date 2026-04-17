from unittest.mock import patch

from tests.config import (
    GET_FW_VERSION,
    GET_FW_VERSION_UNSUPPORTED,
    GET_NIC_ATTR_LIST,
    GET_NIC_ATTR_LIST_UPDATED,
    GET_NIC_ATTR_LIST_INTEGER_UPDATED,
    GET_NIC_ATTR_REGISTRY,
    GET_NIC_FQQDS_ADAPTERS,
    GET_NIC_FQQDS_EMBEDDED,
    GET_NIC_FQQDS_INTEGRATED,
    GET_NIC_FQQDS_SLOT,
    INIT_RESP,
    INIT_RESP_SUPERMICRO,
    JOB_STATUS_SCHEDULED,
    JOB_STATUS_RUNNING,
    JOB_STATUS_COMPLETED,
    JOB_STATUS_FAILED,
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
    RESPONSE_SET_NIC_ATTR_WITH_JOB_SUCCESS,
    RESPONSE_SET_NIC_ATTR_JOB_FAILED,
    RESPONSE_SET_NIC_ATTR_NO_JOB_ID,
    RESPONSE_SET_NIC_ATTR_PRE_REBOOT_FAIL,
    RESPONSE_SET_NIC_ATTR_VERIFY_FAILED,
    RESPONSE_SET_NIC_ATTR_FALSE_NEGATIVE,
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
        assert err == RESPONSE_VENDOR_UNSUPPORTED + "\n"

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
        responses = INIT_RESP + [
            GET_FW_VERSION,
            GET_NIC_ATTR_REGISTRY,
            GET_NIC_ATTR_LIST,
        ]
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
        self.set_mock_response(mock_patch, 200, "OK", headers={})
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
        self.set_mock_response(mock_patch, [503, 200], "OK", headers={})
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
        self.set_mock_response(mock_patch, [400, 200, 200], "OK", headers={})
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
        self.set_mock_response(mock_patch, 200, "OK", headers={})
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
        self.set_mock_response(mock_patch, 200, "OK", headers={})
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
        self.set_mock_response(mock_patch, 200, "OK", headers={})
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
        self.set_mock_response(mock_patch, 200, "OK", headers={})
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

    # ==================== Job Monitoring Tests (Issue #523 Fix) ====================

    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_set_nic_attr_with_job_monitoring_success(self, mock_get, mock_post, mock_delete, mock_patch):
        """Test successful NIC attribute change with full job monitoring"""
        responses = INIT_RESP + [
            GET_FW_VERSION,
            GET_NIC_ATTR_REGISTRY,
            GET_NIC_ATTR_LIST,
            JOB_STATUS_SCHEDULED,  # Pre-reboot job check
            RESET_TYPE_RESP,
            STATE_OFF_RESP,
            JOB_STATUS_COMPLETED,  # Post-reboot job monitoring
            GET_FW_VERSION,
            GET_NIC_ATTR_REGISTRY,
            GET_NIC_ATTR_LIST_UPDATED,  # Final verification
        ]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")

        # Mock PATCH response with Location header containing job ID
        patch_headers = {"Location": "/redfish/v1/Managers/iDRAC.Embedded.1/Jobs/JID_498218641680"}
        self.set_mock_response(mock_patch, 202, "OK", headers=patch_headers)

        self.args = [
            self.option_arg,
            "NIC.Embedded.1-1-1",
            "--attribute",
            "WakeOnLan",
            "--value",
            "Disabled",
        ]
        _, err = self.badfish_call()
        assert err == RESPONSE_SET_NIC_ATTR_WITH_JOB_SUCCESS

    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_set_nic_attr_no_job_id_fallback(self, mock_get, mock_post, mock_delete, mock_patch):
        """Test fallback behavior when no job ID is returned (preserves old behavior)"""
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

        # PATCH succeeds but no Location header
        self.set_mock_response(mock_patch, 202, "OK", headers={})

        self.args = [
            self.option_arg,
            "NIC.Embedded.1-1-1",
            "--attribute",
            "WakeOnLan",
            "--value",
            "Disabled",
        ]
        _, err = self.badfish_call()
        assert err == RESPONSE_SET_NIC_ATTR_NO_JOB_ID

    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_set_nic_attr_job_failed_pre_reboot(self, mock_get, mock_post, mock_delete, mock_patch):
        """Test detection of job failure before reboot"""
        responses = INIT_RESP + [
            GET_FW_VERSION,
            GET_NIC_ATTR_REGISTRY,
            GET_NIC_ATTR_LIST,
            JOB_STATUS_FAILED,  # Job already failed before reboot
        ]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")

        patch_headers = {"Location": "/redfish/v1/Managers/iDRAC.Embedded.1/Jobs/JID_498218641680"}
        self.set_mock_response(mock_patch, 202, "OK", headers=patch_headers)

        self.args = [
            self.option_arg,
            "NIC.Embedded.1-1-1",
            "--attribute",
            "WakeOnLan",
            "--value",
            "Disabled",
        ]
        _, err = self.badfish_call()
        assert err == RESPONSE_SET_NIC_ATTR_PRE_REBOOT_FAIL

    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_set_nic_attr_job_completed_but_value_not_changed(self, mock_get, mock_post, mock_delete, mock_patch):
        """Test detection when job completes but value didn't actually change"""
        responses = INIT_RESP + [
            GET_FW_VERSION,
            GET_NIC_ATTR_REGISTRY,
            GET_NIC_ATTR_LIST,
            JOB_STATUS_SCHEDULED,  # Pre-reboot
            RESET_TYPE_RESP,
            STATE_OFF_RESP,
            JOB_STATUS_COMPLETED,  # Job says success
            GET_FW_VERSION,
            GET_NIC_ATTR_REGISTRY,
            GET_NIC_ATTR_LIST,  # But value is still old value (Enabled)
        ]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")

        patch_headers = {"Location": "/redfish/v1/Managers/iDRAC.Embedded.1/Jobs/JID_498218641680"}
        self.set_mock_response(mock_patch, 202, "OK", headers=patch_headers)

        self.args = [
            self.option_arg,
            "NIC.Embedded.1-1-1",
            "--attribute",
            "WakeOnLan",
            "--value",
            "Disabled",
        ]
        _, err = self.badfish_call()
        assert err == RESPONSE_SET_NIC_ATTR_VERIFY_FAILED

    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_set_nic_attr_job_failed_but_value_changed(self, mock_get, mock_post, mock_delete, mock_patch):
        """Test false negative detection: job reports failure but value actually changed"""
        responses = INIT_RESP + [
            GET_FW_VERSION,
            GET_NIC_ATTR_REGISTRY,
            GET_NIC_ATTR_LIST,
            JOB_STATUS_SCHEDULED,  # Pre-reboot
            RESET_TYPE_RESP,
            STATE_OFF_RESP,
            JOB_STATUS_FAILED,  # Job reports failure
            GET_FW_VERSION,  # But verification shows value DID change
            GET_NIC_ATTR_REGISTRY,
            GET_NIC_ATTR_LIST_UPDATED,
        ]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")

        patch_headers = {"Location": "/redfish/v1/Managers/iDRAC.Embedded.1/Jobs/JID_498218641680"}
        self.set_mock_response(mock_patch, 202, "OK", headers=patch_headers)

        self.args = [
            self.option_arg,
            "NIC.Embedded.1-1-1",
            "--attribute",
            "WakeOnLan",
            "--value",
            "Disabled",
        ]
        _, err = self.badfish_call()
        assert err == RESPONSE_SET_NIC_ATTR_FALSE_NEGATIVE

    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_set_nic_attr_integer_with_job_monitoring(self, mock_get, mock_post, mock_delete, mock_patch):
        """Test integer attribute with job monitoring - Issue #523 scenario"""
        responses = INIT_RESP + [
            GET_FW_VERSION,
            GET_NIC_ATTR_REGISTRY,
            GET_NIC_ATTR_LIST,  # BlnkLeds: 0
            JOB_STATUS_SCHEDULED,
            RESET_TYPE_RESP,
            STATE_OFF_RESP,
            JOB_STATUS_COMPLETED,
            GET_FW_VERSION,
            GET_NIC_ATTR_REGISTRY,
            GET_NIC_ATTR_LIST_INTEGER_UPDATED,  # BlnkLeds: 12
        ]
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")

        patch_headers = {"Location": "/redfish/v1/Managers/iDRAC.Embedded.1/Jobs/JID_498218641680"}
        self.set_mock_response(mock_patch, 202, "OK", headers=patch_headers)

        self.args = [
            self.option_arg,
            "NIC.Embedded.1-1-1",
            "--attribute",
            "BlnkLeds",
            "--value",
            "12",
        ]
        _, err = self.badfish_call()
        # Should succeed with job monitoring
        assert "✓ Successfully changed BlnkLeds" in err
        assert "from 0 to 12" in err

    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_set_nic_attr_empty_location_header(self, mock_get, mock_post, mock_delete, mock_patch):
        """Test handling of empty Location header"""
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

        # Location header present but empty
        patch_headers = {"Location": ""}
        self.set_mock_response(mock_patch, 202, "OK", headers=patch_headers)

        self.args = [
            self.option_arg,
            "NIC.Embedded.1-1-1",
            "--attribute",
            "WakeOnLan",
            "--value",
            "Disabled",
        ]
        _, err = self.badfish_call()
        # Should fall back to old behavior with warning
        assert "No job ID returned in Location header" in err
        assert "Configuration change submitted but job monitoring was not possible" in err
