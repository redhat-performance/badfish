from unittest.mock import patch

from tests.config import (
    FIRMWARE_INVENTORY_1_RESP,
    FIRMWARE_INVENTORY_2_RESP,
    FIRMWARE_INVENTORY_RESP,
    FIRMWARE_INVENTORY_RESP_CONTAINING_ERROR,
    INIT_RESP,
    RESPONSE_FIRMWARE_INVENTORY,
    RESPONSE_FIRMWARE_INVENTORY_NONE_RESPONSE,
    RESPONSE_FIRMWARE_INVENTORY_NOT_ABLE_TO_ACCESS,
)
from tests.test_base import MockResponse, TestBase


class TestFirmwareInventory(TestBase):
    option_arg = "--firmware-inventory"

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_firmware_inventory(self, mock_get, mock_post, mock_delete):
        responses_add = [
            FIRMWARE_INVENTORY_RESP,
            FIRMWARE_INVENTORY_1_RESP,
            FIRMWARE_INVENTORY_2_RESP,
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_FIRMWARE_INVENTORY

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_firmware_inventory_json_invalid(self, mock_get, mock_post, mock_delete):
        responses_add = [""]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_FIRMWARE_INVENTORY_NOT_ABLE_TO_ACCESS

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    def test_firmware_inventory_json_contains_error(self, mock_get, mock_post, mock_delete):
        responses_add = [FIRMWARE_INVENTORY_RESP_CONTAINING_ERROR]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_FIRMWARE_INVENTORY_NOT_ABLE_TO_ACCESS

    @patch("aiohttp.ClientSession.delete")
    @patch("aiohttp.ClientSession.post")
    @patch("aiohttp.ClientSession.get")
    @patch("badfish.main.Badfish.get_request")
    def test_firmware_inventory_none_response(self, mock_get_req_call, mock_get, mock_post, mock_delete):
        mock_get_req_call.side_effect = [
            MockResponse(FIRMWARE_INVENTORY_RESP, 200),  # Firmware inventory list
            MockResponse(FIRMWARE_INVENTORY_1_RESP, 200),  # First device details
            None,  # Second device fails
        ]
        self.set_mock_response(mock_get, 200, INIT_RESP)
        self.set_mock_response(mock_post, 200, "OK")
        self.set_mock_response(mock_delete, 200, "OK")
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_FIRMWARE_INVENTORY_NONE_RESPONSE
