import pytest

from tests.test_base import TestBase
from tests import config


class TestCheckBoot(TestBase):
    option_arg = "--check-boot"

    @pytest.mark.skip(reason="Needs to be transformed to async")
    def test_check_boot_without_interfaces(self):
        self.boot_seq = config.BOOT_SEQ_RESPONSE_DIRECTOR
        self.args = [self.option_arg]
        _, err = self.badfish_call()
        assert config.RESPONSE_WITHOUT == err

    @pytest.mark.skip(reason="Needs to be transformed to async")
    def test_check_boot_with_interfaces_director(self):
        self.boot_seq = config.BOOT_SEQ_RESPONSE_DIRECTOR
        self.args = ["-i", config.INTERFACES_PATH, self.option_arg]
        _, err = self.badfish_call()
        assert config.RESPONSE_DIRECTOR == err

    @pytest.mark.skip(reason="Needs to be transformed to async")
    def test_check_boot_with_interfaces_foreman(self):
        self.boot_seq = config.BOOT_SEQ_RESPONSE_FOREMAN
        self.args = ["-i", config.INTERFACES_PATH, self.option_arg]
        _, err = self.badfish_call()
        assert config.RESPONSE_FOREMAN == err

    @pytest.mark.skip(reason="Needs to be transformed to async")
    def test_check_boot_no_match(self):
        self.boot_seq = config.BOOT_SEQ_RESPONSE_NO_MATCH
        self.args = ["-i", config.INTERFACES_PATH, self.option_arg]
        _, err = self.badfish_call()
        assert config.WARN_NO_MATCH == err
