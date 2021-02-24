from asynctest import patch
from tests.config import (
    INIT_RESP,
    RESPONSE_WITHOUT,
    NETWORK_ADAPTERS_RESP,
    NETWORK_PORTS_RESP,
    NETWORK_DEV_FUNC_RESP,
    NETWORK_DEV_FUNC_DET_RESP,
    NETWORK_PORTS_ROOT_RESP,
    DEVICE_NIC_I,
    DEVICE_NIC_S, RESPONSE_LS_INTERFACES,
)
from tests.test_base import TestBase


class TestCheckBoot(TestBase):
    option_arg = "--ls-interfaces"

    @patch("aiohttp.ClientSession.get")
    def test_check_boot_without_interfaces(self, mock_get):
        responses_add = [
            NETWORK_ADAPTERS_RESP,
            NETWORK_PORTS_ROOT_RESP % (DEVICE_NIC_I, DEVICE_NIC_I),
            NETWORK_DEV_FUNC_RESP % (DEVICE_NIC_I, DEVICE_NIC_I),
            NETWORK_PORTS_RESP % DEVICE_NIC_I,
            NETWORK_DEV_FUNC_DET_RESP,
            NETWORK_PORTS_ROOT_RESP % (DEVICE_NIC_S, DEVICE_NIC_S),
            NETWORK_DEV_FUNC_RESP % (DEVICE_NIC_S, DEVICE_NIC_S),
            NETWORK_PORTS_RESP % DEVICE_NIC_S,
            NETWORK_DEV_FUNC_DET_RESP,
        ]
        responses = INIT_RESP + responses_add
        self.set_mock_response(mock_get, 200, responses)
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert err == RESPONSE_LS_INTERFACES

