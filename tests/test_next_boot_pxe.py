from asynctest import patch
from tests.config import (
    INIT_RESP,
    BIOS_RESPONSE_OK,
    NEXT_BOOT_PXE_OK, NEXT_BOOT_PXE_BAD,
)
from tests.test_base import TestBase


class TestNextBootPxe(TestBase):
    option_arg = "--pxe"

    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.get")
    def test_next_boot_pxe_ok(self, mock_get, mock_patch):
        responses = INIT_RESP
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_patch, 200, ["OK"])
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == NEXT_BOOT_PXE_OK

    @patch("aiohttp.ClientSession.patch")
    @patch("aiohttp.ClientSession.get")
    def test_next_boot_pxe_bad(self, mock_get, mock_patch):
        responses = INIT_RESP
        self.set_mock_response(mock_get, 200, responses)
        self.set_mock_response(mock_patch, 400, ["NOT OK"])
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == NEXT_BOOT_PXE_BAD
