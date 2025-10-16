from unittest.mock import patch

from tests.config import (
    BAD_DEVICE_NAME,
    BIOS_REGISTRY_OK,
    BLANK_RESP,
    BOOT_MODE_NO_RESP,
    BOOT_MODE_RESP,
    BOOT_MODE_RESP_UEFI,
    BOOT_SEQ_RESP,
    BOOT_SEQ_RESPONSE_DIRECTOR,
    BOOT_SEQ_RESPONSE_FOREMAN,
    BOOT_SEQ_RESPONSE_FOREMAN_SHORTER,
    DEVICE_NIC_2,
    INIT_RESP,
    INTERFACES_PATH,
    JOB_OK_RESP,
    PXE_DEV_RESP,
    RESET_TYPE_RESP,
    RESPONSE_CHANGE_BAD_TYPE,
    RESPONSE_CHANGE_BOOT,
    RESPONSE_CHANGE_BOOT_WITH_BIOS_WARNINGS,
    RESPONSE_CHANGE_BOOT_INCORRECT_PATH,
    RESPONSE_CHANGE_BOOT_LESS_VALID_DEVICES,
    RESPONSE_CHANGE_BOOT_PATCH_ERROR,
    RESPONSE_CHANGE_BOOT_PXE,
    RESPONSE_CHANGE_BOOT_UEFI,
    RESPONSE_CHANGE_NO_INT,
    RESPONSE_CHANGE_TO_SAME,
    STATE_ON_RESP,
    TOGGLE_DEV_NO_MATCH,
    TOGGLE_DEV_OK,
)
from tests.test_base import TestBase


class TestChangeBoot(TestBase):
    option_arg = "-t"
    boot_seq_resp_fmt_dir = BOOT_SEQ_RESP % str(BOOT_SEQ_RESPONSE_DIRECTOR)
    boot_seq_resp_fmt_for = BOOT_SEQ_RESP % str(BOOT_SEQ_RESPONSE_FOREMAN)

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.get")
    def test_change_to_foreman(self, mock_get, mock_patch, mock_post, mock_delete):
        get_resp = [
            BOOT_MODE_RESP,
            self.boot_seq_resp_fmt_dir.replace("'", '"'),
            BLANK_RESP,
            BOOT_MODE_RESP,
            BOOT_MODE_RESP,
            RESET_TYPE_RESP,
            STATE_ON_RESP,
            STATE_ON_RESP,
        ]
        responses = INIT_RESP + get_resp
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_patch, 200, ["OK"])
        self.set_mock_response(mock_post, 200, JOB_OK_RESP)
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = ["-i", INTERFACES_PATH, self.option_arg, "foreman"]
        _, err = self.badfish_call()
        assert err == RESPONSE_CHANGE_BOOT

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_change_boot_incorrect_path(self, mock_get, mock_post, mock_delete):
        responses = INIT_RESP
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = ["-i", "INCORRECT PATH", self.option_arg, "foreman"]
        _, err = self.badfish_call()
        assert err == RESPONSE_CHANGE_BOOT_INCORRECT_PATH

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.get")
    def test_change_boot_patch_error(self, mock_get, mock_patch, mock_post, mock_delete):
        get_resp = [
            BOOT_MODE_RESP,
            self.boot_seq_resp_fmt_dir.replace("'", '"'),
            BLANK_RESP,
            BOOT_MODE_RESP_UEFI,
            BOOT_MODE_RESP,
            RESET_TYPE_RESP,
            STATE_ON_RESP,
            STATE_ON_RESP,
        ]
        responses = INIT_RESP + get_resp
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_patch, 400, "OK")
        self.set_mock_response(mock_post, 200, JOB_OK_RESP)
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = ["-i", INTERFACES_PATH, self.option_arg, "foreman"]
        _, err = self.badfish_call()
        assert err == RESPONSE_CHANGE_BOOT_PATCH_ERROR

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.get")
    def test_change_boot_less_valid_devices(self, mock_get, mock_patch, mock_post, mock_delete):
        boot_seq_resp_fmt_for = BOOT_SEQ_RESP % str(BOOT_SEQ_RESPONSE_FOREMAN_SHORTER)
        get_resp = [
            BOOT_MODE_RESP,
            boot_seq_resp_fmt_for.replace("'", '"'),
            BLANK_RESP,
            BOOT_MODE_RESP_UEFI,  # 689
            BOOT_MODE_RESP,  # 703
            RESET_TYPE_RESP,
            STATE_ON_RESP,
            STATE_ON_RESP,
        ]
        responses = INIT_RESP + get_resp
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_patch, 200, "OK")
        self.set_mock_response(mock_post, 200, JOB_OK_RESP)
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = ["-i", INTERFACES_PATH, self.option_arg, "foreman"]
        _, err = self.badfish_call()
        assert err == RESPONSE_CHANGE_BOOT_LESS_VALID_DEVICES

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.get")
    def test_change_boot_pxe(self, mock_get, mock_patch, mock_post, mock_delete):
        get_resp = [
            BOOT_MODE_RESP,
            self.boot_seq_resp_fmt_dir.replace("'", '"'),
            BLANK_RESP,
            BOOT_MODE_RESP,
            BOOT_MODE_RESP,
            RESET_TYPE_RESP,
            STATE_ON_RESP,
            STATE_ON_RESP,
        ]
        responses = INIT_RESP + get_resp
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_patch, 200, "OK")
        self.set_mock_response(mock_post, 200, JOB_OK_RESP)
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = ["-i", INTERFACES_PATH, self.option_arg, "foreman", "--pxe"]
        _, err = self.badfish_call()
        assert err == RESPONSE_CHANGE_BOOT_PXE

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.get")
    def test_change_to_director(self, mock_get, mock_patch, mock_post, mock_delete):
        get_resp = [
            BOOT_MODE_RESP,
            self.boot_seq_resp_fmt_for.replace("'", '"'),
            BLANK_RESP,
            BOOT_MODE_RESP,
            BOOT_MODE_RESP,
            RESET_TYPE_RESP,
            STATE_ON_RESP,
            STATE_ON_RESP,
        ]
        responses = INIT_RESP + get_resp
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_patch, 200, ["OK"])
        self.set_mock_response(mock_post, 200, JOB_OK_RESP)
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = ["-i", INTERFACES_PATH, self.option_arg, "director"]
        _, err = self.badfish_call()
        assert err == RESPONSE_CHANGE_BOOT

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.get")
    def test_change_to_uefi(self, mock_get, mock_patch, mock_post, mock_delete):
        get_resp = [
            BOOT_MODE_RESP,
            BOOT_MODE_RESP,
            BIOS_REGISTRY_OK.replace("'", '"'),
            BOOT_MODE_RESP,
        ]
        get_resp = get_resp + [PXE_DEV_RESP for _ in range(6)]
        get_resp.append(BOOT_MODE_RESP)
        get_resp = get_resp + [PXE_DEV_RESP for _ in range(5)]
        get_resp = get_resp + [
            RESET_TYPE_RESP,
            STATE_ON_RESP,
            STATE_ON_RESP,
        ]
        responses = INIT_RESP + get_resp
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_patch, 200, ["OK"])
        self.set_mock_response(mock_post, 200, JOB_OK_RESP)
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = ["-i", INTERFACES_PATH, self.option_arg, "uefi"]
        _, err = self.badfish_call()
        assert err == RESPONSE_CHANGE_BOOT_UEFI

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.get")
    def test_change_to_director_no_boot(self, mock_get, mock_patch, mock_post, mock_delete):
        get_resp = [
            BOOT_MODE_NO_RESP,
            self.boot_seq_resp_fmt_for.replace("'", '"'),
            BLANK_RESP,
            BOOT_MODE_RESP,
            BOOT_MODE_RESP,
            RESET_TYPE_RESP,
            STATE_ON_RESP,
            STATE_ON_RESP,
        ]
        responses = INIT_RESP + get_resp
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_patch, 200, ["OK"])
        self.set_mock_response(mock_post, 200, JOB_OK_RESP)
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = ["-i", INTERFACES_PATH, self.option_arg, "director"]
        _, err = self.badfish_call()
        assert err == RESPONSE_CHANGE_BOOT_WITH_BIOS_WARNINGS

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_change_bad_type(self, mock_get, mock_post, mock_delete):
        get_resp = [
            BOOT_MODE_RESP,
            self.boot_seq_resp_fmt_for.replace("'", '"'),
            BLANK_RESP,
            STATE_ON_RESP,
            BOOT_MODE_RESP,
            STATE_ON_RESP,
            STATE_ON_RESP,
        ]
        responses = INIT_RESP + get_resp
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = ["-i", INTERFACES_PATH, self.option_arg, "bad_type"]
        _, err = self.badfish_call()
        assert err == RESPONSE_CHANGE_BAD_TYPE

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.get")
    def test_change_to_same(self, mock_get, mock_patch, mock_post, mock_delete):
        get_resp = [
            BOOT_MODE_RESP,
            self.boot_seq_resp_fmt_dir.replace("'", '"'),
            BLANK_RESP,
            STATE_ON_RESP,
            BOOT_MODE_RESP,
            STATE_ON_RESP,
            STATE_ON_RESP,
        ]
        responses = INIT_RESP + get_resp
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_patch, 200, ["OK"])
        self.set_mock_response(mock_post, 200, JOB_OK_RESP)
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = ["-i", INTERFACES_PATH, self.option_arg, "director"]
        _, err = self.badfish_call()
        assert err == RESPONSE_CHANGE_TO_SAME

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.get")
    def test_change_no_interfaces(self, mock_get, mock_patch, mock_post, mock_delete):
        get_resp = [
            BOOT_MODE_RESP,
            self.boot_seq_resp_fmt_for.replace("'", '"'),
            BLANK_RESP,
            STATE_ON_RESP,
            BOOT_MODE_RESP,
            STATE_ON_RESP,
            STATE_ON_RESP,
        ]
        responses = INIT_RESP + get_resp
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_patch, 200, ["OK"])
        self.set_mock_response(mock_post, 200, JOB_OK_RESP)
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg, "director"]
        _, err = self.badfish_call()
        assert err == RESPONSE_CHANGE_NO_INT


class TestToggleDevice(TestBase):
    option_arg = "--toggle-boot-device"
    boot_seq_resp_fmt = BOOT_SEQ_RESP % str(BOOT_SEQ_RESPONSE_DIRECTOR)

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.get")
    def test_toggle_ok(self, mock_get, mock_patch, mock_post, mock_delete):
        get_resp = [
            BOOT_MODE_RESP,
            self.boot_seq_resp_fmt.replace("'", '"'),
            BOOT_MODE_RESP,
            RESET_TYPE_RESP,
            STATE_ON_RESP,
            STATE_ON_RESP,
        ]
        responses = INIT_RESP + get_resp
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_patch, 200, ["OK"])
        self.set_mock_response(mock_post, 200, JOB_OK_RESP)
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg, DEVICE_NIC_2["name"]]
        _, err = self.badfish_call()
        assert err == TOGGLE_DEV_OK

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.get")
    def test_toggle_bad_device(self, mock_get, mock_patch, mock_post, mock_delete):
        get_resp = [
            BOOT_MODE_RESP,
            self.boot_seq_resp_fmt.replace("'", '"'),
            BLANK_RESP,
        ]
        responses = INIT_RESP + get_resp
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_patch, 200, ["OK"])
        self.set_mock_response(mock_post, 200, JOB_OK_RESP)
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg, BAD_DEVICE_NAME]
        _, err = self.badfish_call()
        assert err == TOGGLE_DEV_NO_MATCH
