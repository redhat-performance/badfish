from tests.test_base import TestBase
from tests import config


class TestResetIdrac(TestBase):
    option_arg = "--racreset"

    def test_reset_idrac(self):
        self.boot_seq = config.BOOT_SEQ_RESPONSE_DIRECTOR
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert config.RESPONSE_RESET == err
