import os

MOCK_HOST = "r630.host.io"
MOCK_USER = "mock_user"
MOCK_PASS = "mock_pass"


def render_device_dict(index, device):
    device_dict = {
        u'Index': index,
        u'Enabled': True,
        u'Id': u'BIOS.Setup.1-1#BootSeq#{name}#{hash}'.format(**device),
        u'Name': device['name']
    }
    return device_dict


DEVICE_HDD_1 = {'name': u'HardDisk.List.1-1', 'hash': 'c9203080df84781e2ca3d512883dee6f'}
DEVICE_NIC_1 = {'name': u'NIC.Integrated.1-2-1', 'hash': 'bfa8fe2210d216298c7c53aedfc7e21b'}
DEVICE_NIC_2 = {'name': u'NIC.Slot.2-1-1', 'hash': '135ac45c488549c04a21f1c199c2044a'}

BOOT_SEQ_RESPONSE_DIRECTOR = [
    render_device_dict(0, DEVICE_NIC_1),
    render_device_dict(1, DEVICE_HDD_1),
    render_device_dict(2, DEVICE_NIC_2)
]
BOOT_SEQ_RESPONSE_FOREMAN = [
    render_device_dict(0, DEVICE_NIC_2),
    render_device_dict(1, DEVICE_HDD_1),
    render_device_dict(2, DEVICE_NIC_1)
]
BOOT_SEQ_RESPONSE_NO_MATCH = [
    render_device_dict(0, DEVICE_HDD_1),
    render_device_dict(1, DEVICE_NIC_1),
    render_device_dict(2, DEVICE_NIC_2)
]

RESPONSE_WITHOUT = '- INFO     - Current boot order:\n' \
                   '- INFO     - 1: NIC.Integrated.1-2-1\n' \
                   '- INFO     - 2: HardDisk.List.1-1\n' \
                   '- INFO     - 3: NIC.Slot.2-1-1\n'
RESPONSE_NO_MATCH = '- INFO     - Current boot order:\n' \
                    '- INFO     - 1: HardDisk.List.1-1\n' \
                    '- INFO     - 2: NIC.Integrated.1-2-1\n' \
                    '- INFO     - 3: NIC.Slot.2-1-1\n'
WARN_NO_MATCH = '- WARNING  - Current boot order does not match any of the given.\n%s' % RESPONSE_NO_MATCH
RESPONSE_DIRECTOR = "- INFO     - Current boot order is set to 'director'.\n"

RESPONSE_FOREMAN = "- INFO     - Current boot order is set to 'foreman'.\n"
INTERFACES_PATH = os.path.join(os.path.dirname(__file__), "../config/idrac_interfaces.yml")
