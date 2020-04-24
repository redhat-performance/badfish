import os

MOCK_HOST = "000-r630.host.io"
MOCK_USER = "mock_user"
MOCK_PASS = "mock_pass"


def render_device_dict(index, device):
    device_dict = {
        "Index": index,
        "Enabled": "True",
        "Id": "BIOS.Setup.1-1#BootSeq#{name}#{hash}".format(**device),
        "Name": device["name"],
    }
    return device_dict


DEVICE_HDD_1 = {"name": "HardDisk.List.1-1", "hash": "c9203080df84781e2ca3d512883dee6f"}
DEVICE_NIC_1 = {
    "name": "NIC.Integrated.1-2-1",
    "hash": "bfa8fe2210d216298c7c53aedfc7e21b",
}
DEVICE_NIC_2 = {"name": "NIC.Slot.2-1-1", "hash": "135ac45c488549c04a21f1c199c2044a"}

BOOT_SEQ_RESPONSE_DIRECTOR = [
    render_device_dict(0, DEVICE_NIC_1),
    render_device_dict(1, DEVICE_HDD_1),
    render_device_dict(2, DEVICE_NIC_2),
]
BOOT_SEQ_RESPONSE_FOREMAN = [
    render_device_dict(0, DEVICE_NIC_2),
    render_device_dict(1, DEVICE_HDD_1),
    render_device_dict(2, DEVICE_NIC_1),
]
BOOT_SEQ_RESPONSE_NO_MATCH = [
    render_device_dict(0, DEVICE_HDD_1),
    render_device_dict(1, DEVICE_NIC_1),
    render_device_dict(2, DEVICE_NIC_2),
]

RESPONSE_WITHOUT = (
    "- INFO     - Systems service: /redfish/v1/Systems/System.Embedded.1.\n"
    "- INFO     - Managers service: /redfish/v1/Managers/iDRAC.Embedded.1.\n"
    "- INFO     - Current boot order:\n"
    "- INFO     - 1: NIC.Integrated.1-2-1\n"
    "- INFO     - 2: HardDisk.List.1-1\n"
    "- INFO     - 3: NIC.Slot.2-1-1\n"
)
RESPONSE_NO_MATCH = (
    "- INFO     - Current boot order:\n"
    "- INFO     - 1: HardDisk.List.1-1\n"
    "- INFO     - 2: NIC.Integrated.1-2-1\n"
    "- INFO     - 3: NIC.Slot.2-1-1\n"
)
WARN_NO_MATCH = (
        "- INFO     - Systems service: /redfish/v1/Systems/System.Embedded.1.\n"
        "- INFO     - Managers service: /redfish/v1/Managers/iDRAC.Embedded.1.\n"
        "- WARNING  - Current boot order does not match any of the given.\n%s"
        % RESPONSE_NO_MATCH
)
RESPONSE_DIRECTOR = (
    "- INFO     - Systems service: /redfish/v1/Systems/System.Embedded.1.\n"
    "- INFO     - Managers service: /redfish/v1/Managers/iDRAC.Embedded.1.\n"
    "- WARNING  - Current boot order is set to: director.\n"
)

RESPONSE_FOREMAN = (
    "- INFO     - Systems service: /redfish/v1/Systems/System.Embedded.1.\n"
    "- INFO     - Managers service: /redfish/v1/Managers/iDRAC.Embedded.1.\n"
    "- WARNING  - Current boot order is set to: foreman.\n"
)
INTERFACES_PATH = os.path.join(
    os.path.dirname(__file__), "../config/idrac_interfaces.yml"
)

# test_boot_to constants
BAD_DEVICE_NAME = "BadIF.Slot.x-y-z"
ERROR_DEV_NO_MATCH = (
        "- ERROR    - Device %s does not match any of the existing for host %s"
        % (BAD_DEVICE_NAME, MOCK_HOST)
)
JOB_ID = "JID_498218641680"
RESPONSE_BOOT_TO = (
    "- INFO     - Systems service: /redfish/v1/Systems/System.Embedded.1.\n"
    "- INFO     - Managers service: /redfish/v1/Managers/iDRAC.Embedded.1.\n"
    f"- WARNING  - Job queue already cleared for iDRAC {MOCK_HOST}, DELETE command will not execute.\n"
    "- INFO     - Command passed to set BIOS attribute pending values.\n"
    "- INFO     - POST command passed to create target config job.\n"
    f"- INFO     - {JOB_ID} job ID successfully created.\n"
    "- INFO     - Command passed to check job status, code 200 returned.\n"
    f"- INFO     - Job id {JOB_ID} successfully scheduled.\n"
    "- INFO     - Command passed to ForceOff server, code return is 204.\n"
    "- INFO     - Polling for host state: Not Down\n"
    "- INFO     - Command passed to On server, code return is 204.\n"
)

# test_reboot_only
RESPONSE_REBOOT_ONLY_SUCCESS = (
    "- INFO     - Systems service: /redfish/v1/Systems/System.Embedded.1.\n"
    "- INFO     - Managers service: /redfish/v1/Managers/iDRAC.Embedded.1.\n"
    "- INFO     - Command passed to GracefulRestart server, code return is 204.\n"
    "- INFO     - Polling for host state: Off\n"
    "- INFO     - Polling for host state: Not Down\n"
    "- INFO     - Command passed to On server, code return is 204.\n"
)

# test_reset_idrac
RESPONSE_RESET = (
    "- INFO     - Systems service: /redfish/v1/Systems/System.Embedded.1.\n"
    "- INFO     - Managers service: /redfish/v1/Managers/iDRAC.Embedded.1.\n"
    "- INFO     - Status code 204 returned for POST command to reset iDRAC.\n"
    "- INFO     - iDRAC will now reset and be back online within a few minutes.\n"
)

# test_change_boot
RESPONSE_CHANGE_BOOT = (
    "- INFO     - Systems service: /redfish/v1/Systems/System.Embedded.1.\n"
    "- INFO     - Managers service: /redfish/v1/Managers/iDRAC.Embedded.1.\n"
    f"- WARNING  - Job queue already cleared for iDRAC {MOCK_HOST}, DELETE command will not "
    "execute.\n"
    "- WARNING  - Waiting for host to be up.\n"
    "- INFO     - Polling for host state: On\n"
    "- INFO     - PATCH command passed to update boot order.\n"
    "- INFO     - POST command passed to create target config job.\n"
    "- INFO     - JID_498218641680 job ID successfully created.\n"
    "- INFO     - Command passed to check job status, code 200 returned.\n"
    "- INFO     - Job id JID_498218641680 successfully scheduled.\n"
    "- INFO     - Command passed to On server, code return is 204.\n"
)
RESPONSE_CHANGE_NO_INT = (
    "- INFO     - Systems service: /redfish/v1/Systems/System.Embedded.1.\n"
    "- INFO     - Managers service: /redfish/v1/Managers/iDRAC.Embedded.1.\n"
    "- WARNING  - No changes were made since the boot order already matches the requested.\n"
)

ROOT_RESP = '{"Managers":{"@odata.id":"/redfish/v1/Managers"},"Systems":{"@odata.id":"/redfish/v1/Systems"}}'
SYS_RESP = '{"Members":[{"@odata.id":"/redfish/v1/Systems/System.Embedded.1"}]}'
MAN_RESP = '{"Members":[{"@odata.id":"/redfish/v1/Managers/iDRAC.Embedded.1"}]}'
RESET_TYPE_RESP = (
    '{"Actions":{"#Manager.Reset":{"ResetType@Redfish.AllowableValues":["GracefulRestart"],'
    '"target":"/redfish/v1/Managers/iDRAC.Embedded.1/Actions/Manager.Reset"}}} '
)
INIT_RESP = [ROOT_RESP, SYS_RESP, ROOT_RESP, MAN_RESP]

STATE_OFF_RESP = '{"PowerState": "Off"}'
STATE_ON_RESP = '{"PowerState": "On"}'

BOOT_MODE_RESP = '{"Attributes": {"BootMode": "Bios"}}'
BOOT_SEQ_RESP = '{"Attributes": {"BootSeq": %s}}'
