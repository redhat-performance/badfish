from unittest.mock import patch

from tests.config import (
    ATTR_VALUE_BAD,
    ATTR_VALUE_OK,
    ATTRIBUTE_BAD,
    ATTRIBUTE_OK,
    BIOS_GET_ALL_OK,
    BIOS_GET_ONE_BAD,
    BIOS_GET_ONE_OK,
    BIOS_REGISTRY_OK,
    BIOS_RESPONSE_DIS,
    BIOS_RESPONSE_OK,
    BIOS_SET_BAD_ATTR,
    BIOS_SET_BAD_VALUE,
    BIOS_SET_OK,
    INIT_RESP,
    JOB_OK_RESP,
    RESET_TYPE_RESP,
    STATE_ON_RESP,
)
from tests.test_base import TestBase


class TestSetBiosAttribute(TestBase):
    option_arg = "--set-bios-attribute"

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.get")
    def test_set_bios_attribute_ok(self, mock_get, mock_patch, mock_post, mock_delete):
        get_resp = [
            BIOS_REGISTRY_OK.replace("'", '"'),
            BIOS_RESPONSE_DIS,
            RESET_TYPE_RESP,
            STATE_ON_RESP,
            STATE_ON_RESP,
        ]
        responses = INIT_RESP + get_resp
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_patch, 200, ["OK"])
        self.set_mock_response(mock_post, 200, ["OK", JOB_OK_RESP])
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [
            self.option_arg,
            "--attribute",
            ATTRIBUTE_OK,
            "--value",
            ATTR_VALUE_OK,
        ]
        _, err = self.badfish_call()
        assert err == BIOS_SET_OK

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.get")
    def test_set_bios_attribute_bad_value(self, mock_get, mock_patch, mock_post, mock_delete):
        get_resp = [
            BIOS_REGISTRY_OK.replace("'", '"'),
            BIOS_RESPONSE_DIS,
            BIOS_RESPONSE_DIS,
        ]
        responses = INIT_RESP + get_resp
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_patch, 200, ["OK"])
        self.set_mock_response(mock_post, 200, ["OK", JOB_OK_RESP])
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [
            self.option_arg,
            "--attribute",
            ATTRIBUTE_OK,
            "--value",
            ATTR_VALUE_BAD,
        ]
        _, err = self.badfish_call()
        assert err == BIOS_SET_BAD_VALUE

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.get")
    def test_set_bios_attribute_bad_attr(self, mock_get, mock_patch, mock_post, mock_delete):
        get_resp = [
            BIOS_REGISTRY_OK.replace("'", '"'),
            BIOS_RESPONSE_DIS,
        ]
        responses = INIT_RESP + get_resp
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_patch, 200, ["OK"])
        self.set_mock_response(mock_post, 200, ["OK", JOB_OK_RESP])
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [
            self.option_arg,
            "--attribute",
            ATTRIBUTE_BAD,
            "--value",
            ATTR_VALUE_OK,
        ]
        _, err = self.badfish_call()
        assert err == BIOS_SET_BAD_ATTR


class TestGetBiosAttribute(TestBase):
    option_arg = "--get-bios-attribute"

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_get_all_attributes(self, mock_get, mock_post, mock_delete):
        get_resp = [
            BIOS_RESPONSE_OK,
        ]
        responses = INIT_RESP + get_resp
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == BIOS_GET_ALL_OK

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_get_one_attribute_ok(self, mock_get, mock_post, mock_delete):
        get_resp = [
            BIOS_REGISTRY_OK.replace("'", '"'),
            BIOS_RESPONSE_OK,
        ]
        responses = INIT_RESP + get_resp
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg, "--attribute", ATTRIBUTE_OK]
        _, err = self.badfish_call()
        assert err == BIOS_GET_ONE_OK

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_get_one_bad_attribute(self, mock_get, mock_post, mock_delete):
        get_resp = [
            BIOS_REGISTRY_OK.replace("'", '"'),
            BIOS_RESPONSE_OK,
        ]
        responses = INIT_RESP + get_resp
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg, "--attribute", ATTRIBUTE_BAD]
        _, err = self.badfish_call()
        assert err == BIOS_GET_ONE_BAD
