from asynctest import patch
from tests.config import (
    INIT_RESP,
    FIRMWARE_INVENTORY_RESP,
    FIRMWARE_INVENTORY_1_RESP,
    FIRMWARE_INVENTORY_2_RESP,
    RESPONSE_FIRMWARE_INVENTORY,
    RESPONSE_FIRMWARE_INVENTORY_NOT_ABLE_TO_ACCESS,
    FIRMWARE_INVENTORY_RESP_CONTAINING_ERROR,
    RESPONSE_FIRMWARE_INVENTORY_NONE_RESPONSE,
)
from tests.test_base import TestBase, MockResponse


class TestFirmwareInventory(TestBase):
    option_arg = "--firmware-inventory"

    @patch("aiohttp.ClientSession.get")
    def test_firmware_inventory(self, mock_get):
        responses_add = [
            FIRMWARE_INVENTORY_RESP,
            FIRMWARE_INVENTORY_1_RESP,
            FIRMWARE_INVENTORY_2_RESP,
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_FIRMWARE_INVENTORY

    @patch("aiohttp.ClientSession.get")
    def test_firmware_inventory_json_invalid(self, mock_get):
        responses_add = [
            ""
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_FIRMWARE_INVENTORY_NOT_ABLE_TO_ACCESS

    @patch("aiohttp.ClientSession.get")
    def test_firmware_inventory_json_contains_error(self, mock_get):
        responses_add = [
            FIRMWARE_INVENTORY_RESP_CONTAINING_ERROR
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_FIRMWARE_INVENTORY_NOT_ABLE_TO_ACCESS

    @patch("badfish.badfish.Badfish.get_request")
    def test_firmware_inventory_none_response(self, mock_get_req_call):
        responses_add = [
            FIRMWARE_INVENTORY_RESP,
            FIRMWARE_INVENTORY_1_RESP
        ]
        responses = INIT_RESP + responses_add
        mock_get_req_call.side_effect = [
            MockResponse(responses[0], 200),
            MockResponse(responses[0], 200),
            MockResponse(responses[1], 200),
            MockResponse(responses[2], 200),
            MockResponse(responses[3], 200),
            MockResponse(responses[4], 200),
            None,
            MockResponse(responses[5], 200)
        ]
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_FIRMWARE_INVENTORY_NONE_RESPONSE
