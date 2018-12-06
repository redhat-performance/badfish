import os
import unittest

import pytest
import requests_mock

from badfish import main

MOCK_HOST = "r630.host.io"
MOCK_USER = "mock_user"
MOCK_PASS = "mock_pass"
BOOT_SEQ_RESPONSE_DIRECTOR = [
    {
        u'Index': 0,
        u'Enabled': True,
        u'Id': u'BIOS.Setup.1-1#BootSeq#NIC.Integrated.1-2-1#bfa8fe2210d216298c7c53aedfc7e21b',
        u'Name': u'NIC.Integrated.1-2-1'
    }, {
        u'Index': 1,
        u'Enabled': True,
        u'Id': u'BIOS.Setup.1-1#BootSeq#HardDisk.List.1-1#c9203080df84781e2ca3d512883dee6f',
        u'Name': u'HardDisk.List.1-1'
    }, {
        u'Index': 2,
        u'Enabled': True,
        u'Id': u'BIOS.Setup.1-1#BootSeq#NIC.Slot.2-1-1#135ac45c488549c04a21f1c199c2044a',
        u'Name': u'NIC.Slot.2-1-1'
    }
]
BOOT_SEQ_RESPONSE_FOREMAN = [
    {
        u'Index': 0,
        u'Enabled': True,
        u'Id': u'BIOS.Setup.1-1#BootSeq#NIC.Slot.2-1-1#135ac45c488549c04a21f1c199c2044a',
        u'Name': u'NIC.Slot.2-1-1'
    }, {
        u'Index': 1,
        u'Enabled': True,
        u'Id': u'BIOS.Setup.1-1#BootSeq#HardDisk.List.1-1#c9203080df84781e2ca3d512883dee6f',
        u'Name': u'HardDisk.List.1-1'
    }, {
        u'Index': 2,
        u'Enabled': True,
        u'Id': u'BIOS.Setup.1-1#BootSeq#NIC.Integrated.1-2-1#bfa8fe2210d216298c7c53aedfc7e21b',
        u'Name': u'NIC.Integrated.1-2-1'
    }
]
BOOT_SEQ_RESPONSE_NO_MATCH = [
    {
        u'Index': 0,
        u'Enabled': True,
        u'Id': u'BIOS.Setup.1-1#BootSeq#HardDisk.List.1-1#c9203080df84781e2ca3d512883dee6f',
        u'Name': u'HardDisk.List.1-1'
    }, {
        u'Index': 1,
        u'Enabled': True,
        u'Id': u'BIOS.Setup.1-1#BootSeq#NIC.Integrated.1-2-1#bfa8fe2210d216298c7c53aedfc7e21b',
        u'Name': u'NIC.Integrated.1-2-1'
    }, {
        u'Index': 2,
        u'Enabled': True,
        u'Id': u'BIOS.Setup.1-1#BootSeq#NIC.Slot.2-1-1#135ac45c488549c04a21f1c199c2044a',
        u'Name': u'NIC.Slot.2-1-1'
    }
]
RESPONSE_WITHOUT = 'Current boot order:\n1: NIC.Integrated.1-2-1\n2: HardDisk.List.1-1\n3: NIC.Slot.2-1-1\n'
RESPONSE_NO_MATCH = 'Current boot order:\n1: HardDisk.List.1-1\n2: NIC.Integrated.1-2-1\n3: NIC.Slot.2-1-1\n'
WARN_NO_MATCH = '- WARN: Current boot order does not match any of the given.\n%s' % RESPONSE_NO_MATCH
RESPONSE_DIRECTOR = "Current boot order is set to 'director'\n"
RESPONSE_FOREMAN = "Current boot order is set to 'foreman'\n"
INTERFACES_PATH = os.path.join(os.path.dirname(__file__), "../config/idrac_interfaces.yml")


class TestCheckBoot(unittest.TestCase):

    @pytest.fixture(autouse=True)
    def inject_capsys(self, capsys):
        self._capsys = capsys

    @requests_mock.mock()
    def badfish_call(self, _mock):
        _mock.get("https://%s/redfish/v1/Systems/System.Embedded.1/Bios" % MOCK_HOST,
                  json={"Attributes": {"BootMode": u"Bios"}}
                  )
        _mock.get("https://%s/redfish/v1/Systems/System.Embedded.1/BootSources" % MOCK_HOST,
                  json={"Attributes": {"BootSeq": self.boot_seq}})
        argv = ["-H", MOCK_HOST, "-u", MOCK_USER, "-p", MOCK_PASS]
        argv.extend(self.args)
        assert not main(argv)
        out, err = self._capsys.readouterr()
        return err

    def test_check_boot_without_interfaces(self):
        self.boot_seq = BOOT_SEQ_RESPONSE_DIRECTOR
        self.args = ["--check-boot"]
        result = self.badfish_call()
        assert RESPONSE_WITHOUT == result

    def test_check_boot_with_interfaces_director(self):
        self.boot_seq = BOOT_SEQ_RESPONSE_DIRECTOR
        self.args = ["-i", INTERFACES_PATH, "--check-boot"]
        result = self.badfish_call()
        assert RESPONSE_DIRECTOR == result

    def test_check_boot_with_interfaces_foreman(self):
        self.boot_seq = BOOT_SEQ_RESPONSE_FOREMAN
        self.args = ["-i", INTERFACES_PATH, "--check-boot"]
        result = self.badfish_call()
        assert RESPONSE_FOREMAN == result

    def test_check_boot_no_match(self):
        self.boot_seq = BOOT_SEQ_RESPONSE_NO_MATCH
        self.args = ["-i", INTERFACES_PATH, "--check-boot"]
        result = self.badfish_call()
        assert WARN_NO_MATCH == result
