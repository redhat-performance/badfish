import pytest

from tests import config
from tests.test_aiohttp_base import TestBase


class TestChangeBoot(TestBase):
    option_arg = "-t"

    @pytest.mark.skip(reason="Needs to be transformed to async")
    def test_change_to_foreman(self):
        self.boot_seq = config.BOOT_SEQ_RESPONSE_DIRECTOR
        self.args = ["-i", config.INTERFACES_PATH, self.option_arg, "foreman"]
        _, err = self.badfish_call()
        assert config.RESPONSE_CHANGE_BOOT == err

    @pytest.mark.skip(reason="Needs to be transformed to async")
    def test_change_to_director(self):
        self.boot_seq = config.BOOT_SEQ_RESPONSE_FOREMAN
        self.args = ["-i", config.INTERFACES_PATH, self.option_arg, "director"]
        _, err = self.badfish_call()
        assert config.RESPONSE_CHANGE_BOOT == err

    @pytest.mark.skip(reason="Needs to be transformed to async")
    def test_change_bad_type(self):
        self.boot_seq = config.BOOT_SEQ_RESPONSE_FOREMAN
        self.args = ["-i", config.INTERFACES_PATH, self.option_arg, "bad_type"]
        with pytest.raises(SystemExit):
            self.badfish_call()

    @pytest.mark.skip(reason="Needs to be transformed to async")
    def test_change_to_same(self):
        self.boot_seq = config.BOOT_SEQ_RESPONSE_DIRECTOR
        self.args = ["-i", config.INTERFACES_PATH, self.option_arg, "director"]
        _, err = self.badfish_call()
        assert config.RESPONSE_CHANGE_NO_INT == err

    @pytest.mark.skip(reason="Needs to be transformed to async")
    def test_change_no_interfaces(self):
        self.boot_seq = config.BOOT_SEQ_RESPONSE_FOREMAN
        self.args = [self.option_arg, "director"]
        with pytest.raises(SystemExit):
            self.badfish_call()
