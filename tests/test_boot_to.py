import pytest

from tests.test_base import TestBase
from tests import config


class TestCheckBoot(TestBase):
    option_arg = "--boot-to"

    def test_boot_to(self):
        self.boot_seq = config.BOOT_SEQ_RESPONSE_DIRECTOR
        self.args = [self.option_arg, config.DEVICE_NIC_2['name']]
        result = self.badfish_call()
        assert config.RESPONSE_BOOT_TO == result

    def test_boot_to_no_match(self):
        self.expect_fail = True
        self.boot_seq = config.BOOT_SEQ_RESPONSE_DIRECTOR
        self.args = [self.option_arg, config.BAD_DEVICE_NAME]
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            result = self.badfish_call()
            assert pytest_wrapped_e.type == SystemExit
            assert config.ERROR_DEV_NO_MATCH == result
