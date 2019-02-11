from tests.test_base import TestBase
from tests import config


class TestRebootOnly(TestBase):
    option_arg = "--reboot-only"

    def test_reboot_only_success(self):
        self.boot_seq = config.BOOT_SEQ_RESPONSE_DIRECTOR
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert config.RESPONSE_REBOOT_ONLY_SUCCESS == err
