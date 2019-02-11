import pytest

from tests.test_base import TestBase
from tests import config


class TestChangeBoot(TestBase):
    option_arg = "-t"

    def test_change_to_foreman(self):
        self.boot_seq = config.BOOT_SEQ_RESPONSE_DIRECTOR
        self.args = ["-i", config.INTERFACES_PATH, self.option_arg, "foreman"]
        _, err = self.badfish_call()
        print("!!!! %s !!!!" % err)
        assert config.RESPONSE_CHANGE_BOOT == err

    def test_change_to_director(self):
        self.boot_seq = config.BOOT_SEQ_RESPONSE_FOREMAN
        self.args = ["-i", config.INTERFACES_PATH, self.option_arg, "director"]
        _, err = self.badfish_call()
        print("!!!! %s !!!!" % err)
        assert config.RESPONSE_CHANGE_BOOT == err

    def test_change_to_same(self):
        self.boot_seq = config.BOOT_SEQ_RESPONSE_DIRECTOR
        self.args = ["-i", config.INTERFACES_PATH, self.option_arg, "director"]
        _, err = self.badfish_call()
        print("!!!! %s !!!!" % err)
        assert config.RESPONSE_CHANGE_NO_INT == err

    def test_change_no_interfaces(self):
        self.boot_seq = config.BOOT_SEQ_RESPONSE_FOREMAN
        self.args = [self.option_arg, "director"]
        with pytest.raises(SystemExit):
            self.badfish_call()
