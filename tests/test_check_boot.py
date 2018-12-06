import unittest

import pytest
import requests_mock

from badfish import main
import tests.config as conf


class TestCheckBoot(unittest.TestCase):

    @pytest.fixture(autouse=True)
    def inject_capsys(self, capsys):
        self._capsys = capsys

    @requests_mock.mock()
    def badfish_call(self, _mock):
        _mock.get("https://%s/redfish/v1/Systems/System.Embedded.1/Bios" % conf.MOCK_HOST,
                  json={"Attributes": {"BootMode": u"Bios"}}
                  )
        _mock.get("https://%s/redfish/v1/Systems/System.Embedded.1/BootSources" % conf.MOCK_HOST,
                  json={"Attributes": {"BootSeq": self.boot_seq}})
        argv = ["-H", conf.MOCK_HOST, "-u", conf.MOCK_USER, "-p", conf.MOCK_PASS]
        argv.extend(self.args)
        assert not main(argv)
        out, err = self._capsys.readouterr()
        return err

    def test_check_boot_without_interfaces(self):
        self.boot_seq = conf.BOOT_SEQ_RESPONSE_DIRECTOR
        self.args = ["--check-boot"]
        result = self.badfish_call()
        assert conf.RESPONSE_WITHOUT == result

    def test_check_boot_with_interfaces_director(self):
        self.boot_seq = conf.BOOT_SEQ_RESPONSE_DIRECTOR
        self.args = ["-i", conf.INTERFACES_PATH, "--check-boot"]
        result = self.badfish_call()
        assert conf.RESPONSE_DIRECTOR == result

    def test_check_boot_with_interfaces_foreman(self):
        self.boot_seq = conf.BOOT_SEQ_RESPONSE_FOREMAN
        self.args = ["-i", conf.INTERFACES_PATH, "--check-boot"]
        result = self.badfish_call()
        assert conf.RESPONSE_FOREMAN == result

    def test_check_boot_no_match(self):
        self.boot_seq = conf.BOOT_SEQ_RESPONSE_NO_MATCH
        self.args = ["-i", conf.INTERFACES_PATH, "--check-boot"]
        result = self.badfish_call()
        assert conf.WARN_NO_MATCH == result
