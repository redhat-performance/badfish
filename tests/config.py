import base64
import os

MOCK_HOST = "f01-h01-000-r630.host.io"
MOCK_USER = "mock_user"
MOCK_PASS = "mock_pass"
JOB_ID = "JID_498218641680"
BAD_DEVICE_NAME = "BadIF.Slot.x-y-z"
DEVICE_NIC_I = "NIC.Integrated.1"
DEVICE_NIC_S = "NIC.Slot.1"
MAC_ADDRESS = "40:A6:B7:0C:01:A0"


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
DEVICE_OPTICAL_1 = {
    "name": "Optical.iDRACVirtual.1-1",
    "hash": "ak3sjf78u38i2hi29ujudh298duoijd28",
}

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
BOOT_SEQ_RESPONSE_FOREMAN_SHORTER = [
    render_device_dict(0, DEVICE_NIC_1),
]
BOOT_SEQ_RESPONSE_OPTICAL = [
    render_device_dict(0, DEVICE_NIC_1),
    render_device_dict(1, DEVICE_HDD_1),
    render_device_dict(2, DEVICE_NIC_2),
    render_device_dict(3, DEVICE_OPTICAL_1),
]

RESPONSE_WITHOUT = (
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
    "- WARNING  - Current boot order does not match any of the given.\n%s"
    % RESPONSE_NO_MATCH
)
RESPONSE_DIRECTOR = "- WARNING  - Current boot order is set to: director.\n"

RESPONSE_FOREMAN = "- WARNING  - Current boot order is set to: foreman.\n"
INTERFACES_PATH = os.path.join(
    os.path.dirname(__file__), "../config/idrac_interfaces.yml"
)

# test_boot_to constants
ERROR_DEV_NO_MATCH = (
    "- ERROR    - Device %s does not match any of the available boot devices for host %s\n"
    % (BAD_DEVICE_NAME, MOCK_HOST)
)
TOGGLE_DEV_OK = (
    "- INFO     - %s has now been disabled\n"
    "- INFO     - Command passed to ForceOff server, code return is 200.\n"
    "- INFO     - Polling for host state: Not Down\n"
    "- INFO     - Command passed to On server, code return is 200.\n"
    % DEVICE_NIC_2["name"]
)
TOGGLE_DEV_NO_MATCH = (
    "- WARNING  - Accepted device names:\n"
    "- WARNING  - NIC.Integrated.1-2-1\n"
    "- WARNING  - HardDisk.List.1-1\n"
    "- WARNING  - NIC.Slot.2-1-1\n"
    "- ERROR    - Boot device name not found\n"
)
RESPONSE_BOOT_TO = (
    f"- WARNING  - Job queue already cleared for iDRAC {MOCK_HOST}, DELETE command will not execute.\n"
    "- INFO     - Command passed to set BIOS attribute pending values.\n"
)
RESPONSE_BOOT_TO_BAD_TYPE = "- ERROR    - Expected values for -t argument are: ['director', 'foreman', 'uefi']\n"
RESPONSE_BOOT_TO_SERVICE_UNAVAILABLE = (
    f"- WARNING  - Job queue already cleared for iDRAC {MOCK_HOST}, DELETE command will not execute.\n"
    "- ERROR    - Command failed, error code is: 503.\n"
    "- INFO     - Retrying to send one time boot.\n"
    "- INFO     - Command passed to set BIOS attribute pending values.\n"
)
RESPONSE_BOOT_TO_SERVICE_BAD_REQUEST = (
    f"- WARNING  - Job queue already cleared for iDRAC {MOCK_HOST}, DELETE command will not execute.\n"
    "- ERROR    - Command failed, error code is: 400.\n"
    f"- WARNING  - Job queue already cleared for iDRAC {MOCK_HOST}, DELETE command will not execute.\n"
    "- INFO     - Status code 204 returned for POST command to reset iDRAC.\n"
    "- INFO     - iDRAC will now reset and be back online within a few minutes.\n"
    "- INFO     - Polling for host state: On\n"
    "- INFO     - Command passed to set BIOS attribute pending values.\n"
    "- ERROR    - POST command failed to create BIOS config job, status code is 400.\n"
    "- ERROR    - {'JobID': 'JID_498218641680'}\n"
)
RESPONSE_BOOT_TO_SERVICE_ERR_HANDLER = (
    f"- WARNING  - Job queue already cleared for iDRAC {MOCK_HOST}, DELETE command will not execute.\n"
    "- ERROR    - Command failed, error code is: 403.\n"
    "- ERROR    - Error reading response from host.\n"
)

RESPONSE_BOOT_TO_BAD_FILE = "- ERROR    - No such file or directory: bad/bad/file.\n"
RESPONSE_BOOT_TO_NO_FILE = "- ERROR    - You must provide a path to the interfaces yaml via `-i` optional argument.\n"
RESPONSE_BOOT_TO_BAD_MAC = (
    "- ERROR    - MAC Address does not match any of the existing\n"
)

# test_reboot_only
RESPONSE_REBOOT_ONLY_SUCCESS = (
    "- INFO     - Command passed to GracefulRestart server, code return is 204.\n"
    "- INFO     - Polling for host state: Not Down\n"
    "- INFO     - Command passed to On server, code return is 204.\n"
)
RESPONSE_REBOOT_ONLY_FAILED_SEND_RESET = (
    "- ERROR    - Command failed to GracefulRestart server, status code is: 400.\n"
    "- ERROR    - Error reading response from host.\n"
)
RESPONSE_REBOOT_ONLY_SUCCESS_WITH_NG_RT = (
    "- INFO     - Command passed to RestartNow server, code return is 204.\n"
    "- INFO     - Polling for host state: Not Down\n"
    "- INFO     - Command passed to On server, code return is 204.\n"
)
RESPONSE_REBOOT_ONLY_FAILED_GRACE_AND_FORCE = (
    "- WARNING  - Command failed to GracefulRestart server, host appears to be already in that state.\n"
    "- INFO     - Polling for host state: Off\n"
    "- WARNING  - Unable to graceful shutdown the server, will perform forced shutdown now.\n"
    "- WARNING  - Command failed to ForceOff server, host appears to be already in that state.\n"
    "- INFO     - Polling for host state: Not Down\n"
)

# test_power
RESPONSE_POWER_ON_OK = "- INFO     - Command passed to On server, code return is 204.\n"
RESPONSE_POWER_OFF_OK = (
    "- INFO     - Command passed to ForceOff server, code return is 204.\n"
)
RESPONSE_POWER_OFF_NO_STATE = "- ERROR    - Couldn't get power state.\n"
RESPONSE_POWER_OFF_ALREADY = "- WARNING  - Command failed to ForceOff server, host appears to be already in that state.\n"
RESPONSE_POWER_OFF_MISS_STATE = "- ERROR    - Power state not found. Try to racreset.\n"
RESPONSE_POWER_ON_NOT = "- WARNING  - Command failed to On server, host appears to be already in that state.\n"
RESPONSE_POWER_OFF_NONE = (
    "- WARNING  - Power state appears to be already set to 'off'.\n"
)
# test_power_consumed_watts
POWER_CONSUMED_RESP = '{"PowerControl":[{"PowerConsumedWatts":"69"}]}'
NO_POWER = '{}'
RESPONSE_POWER_CONSUMED_OK = '- INFO     - Current watts consumed: 69\n'
RESPONSE_NO_POWER_CONSUMED = '- INFO     - Current watts consumed: N/A. Try to `--racreset`.\n'
RESPONSE_POWER_CONSUMED_404 = '- ERROR    - Operation not supported by vendor.\n'
RESPONSE_POWER_CONSUMED_VAL_ERR = '- ERROR    - Power value outside operating range.\n'
# test_reset_%s
RESPONSE_RESET = (
    "- INFO     - Status code %s returned for POST command to reset %s.\n"
    "- INFO     - %s will now reset and be back online within a few minutes.\n"
)
RESPONSE_RESET_FAIL = (
    "- ERROR    - Status code 400 returned, error is: \nBad Request.\n"
)
RESPONSE_RESET_WRONG_VENDOR = (
    "- WARNING  - Vendor isn't a %s, if you are trying this on a %s, use %s instead.\n"
)

# test_change_boot
RESPONSE_CHANGE_NO_BOOT_PREFIX = (
    "- WARNING  - Could not retrieve Bios Attributes.\n"
    "- WARNING  - Assuming boot mode is Bios.\n"
)
RESPONSE_CHANGE_BOOT = (
    f"- WARNING  - Job queue already cleared for iDRAC {MOCK_HOST}, DELETE command will not "
    "execute.\n"
    "- INFO     - Command passed to ForceOff server, code return is 200.\n"
    "- INFO     - Polling for host state: Not Down\n"
    "- INFO     - Command passed to On server, code return is 200.\n"
)
RESPONSE_CHANGE_BOOT_INCORRECT_PATH = (
    "- ERROR    - No such file or directory: 'INCORRECT PATH'.\n"
)
RESPONSE_CHANGE_BOOT_PATCH_ERROR = (
    f"- WARNING  - Job queue already cleared for iDRAC {MOCK_HOST}, DELETE command will not "
    "execute.\n"
    "- WARNING  - Changes being requested will be valid for Bios BootMode. Current boot mode is set to Uefi.\n"
    "- ERROR    - There was something wrong with your request.\n"
    "- ERROR    - Error reading response from host.\n"
)
RESPONSE_CHANGE_BOOT_LESS_VALID_DEVICES = (
    f"- WARNING  - Job queue already cleared for iDRAC {MOCK_HOST}, DELETE command will not "
    "execute.\n"
    "- WARNING  - Changes being requested will be valid for Bios BootMode. Current boot mode is set to Uefi.\n"
    "- WARNING  - Some interfaces are not valid boot devices. Ignoring: NIC.Slot.2-1-1, HardDisk.List.1-1\n"
    "- WARNING  - No changes were made since the boot order already matches the requested.\n"
    "- WARNING  - Actions resource not found\n"
    "- ERROR    - Power state not found. Try to racreset.\n"
)
RESPONSE_CHANGE_BOOT_PXE = (
    f"- WARNING  - Job queue already cleared for iDRAC {MOCK_HOST}, DELETE command will not "
    "execute.\n"
    '- INFO     - PATCH command passed to set next boot onetime boot device to: "Pxe".\n'
    "- INFO     - Command passed to ForceOff server, code return is 200.\n"
    "- INFO     - Polling for host state: Not Down\n"
    "- INFO     - Command passed to On server, code return is 200.\n"
)
RESPONSE_CHANGE_BOOT_UEFI = (
    f"- WARNING  - Job queue already cleared for iDRAC {MOCK_HOST}, DELETE command will not execute.\n"
    "- WARNING  - Attribute value for PxeDev1Interface is already in that state. IGNORING.\n"
    "- INFO     - Command passed to set BIOS attribute pending values.\n"
    "- INFO     - Command passed to GracefulRestart server, code return is 200.\n"
    "- INFO     - Polling for host state: Not Down\n"
    "- INFO     - Command passed to On server, code return is 200.\n"
)
RESPONSE_CHANGE_BAD_TYPE = "- ERROR    - Expected values for -t argument are: ['director', 'foreman', 'uefi']\n"
RESPONSE_CHANGE_TO_SAME = "- WARNING  - No changes were made since the boot order already matches the requested.\n"
RESPONSE_CHANGE_NO_INT = "- ERROR    - You must provide a path to the interfaces yaml via `-i` optional argument.\n"

ROOT_RESP = (
    '{"Managers":{"@odata.id":"/redfish/v1/Managers"},"Systems":{"@odata.id":"/redfish/v1/Systems"}, '
    '"RedfishVersion": "1.0.2","Oem":{"Dell":{"ServiceTag": "T35T7A6"}}}'
)
ROOT_RESP_SUPERMICRO = (
    '{"Managers":{"@odata.id":"/redfish/v1/Managers"},"Systems":{"@odata.id":"/redfish/v1/Systems"}, '
    '"RedfishVersion": "1.0.2","Oem":{"Supermicro":{}}}'
)
SYS_RESP = '{"Members":[{"@odata.id":"/redfish/v1/Systems/System.Embedded.1"}]}'
MAN_RESP = '{"Members":[{"@odata.id":"/redfish/v1/Managers/iDRAC.Embedded.1"}]}'
RESET_TYPE_RESP = (
    '{"Actions":{"#Manager.Reset":{"ResetType@Redfish.AllowableValues":["GracefulRestart"],'
    '"target":"/redfish/v1/Managers/iDRAC.Embedded.1/Actions/Manager.Reset"}}} '
)
RESET_TYPE_RESP_NO_ALLOWABLE_VALUES = (
    '{"Actions":{"#Manager.Reset":{"target":"/redfish/v1/Managers/1/Actions/Manager.Reset"}}} '
)
RESET_TYPE_NG_RESP = (
    '{"Actions":{"#ComputerSystem.Reset":{"ResetType@Redfish.AllowableValues":["RestartNow"],'
    '"target":"/redfish/v1/Managers/iDRAC.Embedded.1/Actions/Manager.Reset"}}} '
)
INIT_RESP = [ROOT_RESP, ROOT_RESP, SYS_RESP, ROOT_RESP, MAN_RESP]
INIT_RESP_SUPERMICRO = [
    ROOT_RESP_SUPERMICRO,
    ROOT_RESP_SUPERMICRO,
    SYS_RESP,
    ROOT_RESP_SUPERMICRO,
    MAN_RESP,
]

RESPONSE_INIT_CREDENTIALS_UNAUTHORIZED = (
    f"- ERROR    - Failed to authenticate. Verify your credentials for {MOCK_HOST}\n"
)
RESPONSE_INIT_CREDENTIALS_FAILED_COMS = (
    f"- ERROR    - Failed to communicate with {MOCK_HOST}\n"
)
RESPONSE_INIT_SYSTEMS_RESOURCE_UNAUTHORIZED = (
    "- ERROR    - Failed to authenticate. Verify your credentials.\n"
)
RESPONSE_INIT_SYSTEMS_RESOURCE_NOT_FOUND = "- ERROR    - Systems resource not found\n"

STATE_OFF_RESP = '{"PowerState": "Off"}'
STATE_ON_RESP = '{"PowerState": "On"}'
STATE_DOWN_RESP = '{"PowerState": "Down"}'
RESPONSE_POWER_STATE_ON = (
    "- INFO     - Power state:\n" f"- INFO     -     {MOCK_HOST}: 'On'\n"
)
RESPONSE_POWER_STATE_DOWN = (
    "- INFO     - Power state:\n" f"- INFO     -     {MOCK_HOST}: 'Down'\n"
)
RESPONSE_POWER_STATE_EMPTY = "- ERROR    - Power state not found. Try to racreset.\n"

BOOT_MODE_RESP = '{"Attributes": {"BootMode": "Bios"}}'
BOOT_MODE_RESP_UEFI = '{"Attributes": {"BootMode": "UEFI"}}'
PXE_DEV_RESP = (
    '{"Attributes": {'
    '"PxeDev1Interface": "NIC.Integrated.1-2-1", "PxeDev1EnDis": "Disabled",'
    '"PxeDev2Interface": "NIC.Slot.2-1-1", "PxeDev2EnDis": "Disabled",'
    '"PxeDev3Interface": "HardDisk.List.1-1", "PxeDev3EnDis": "Disabled"'
    "}}"
)
BOOT_MODE_NO_RESP = '{"Attributes": {"NoBootMode": ""}}'
BOOT_SEQ_RESP = '{"Attributes": {"BootSeq": %s}}'

ETHERNET_INTERFACES_RESP = (
    '{"Members":['
    '{"@odata.id":"/redfish/v1/Systems/System.Embedded.1/EthernetInterfaces/NIC.Slot.1-1-1"},'
    '{"@odata.id":"/redfish/v1/Systems/System.Embedded.1/EthernetInterfaces/NIC.Integrated.1-1-1"}'
    "]}"
)
ETHERNET_INTERFACES_RESP_NIC_SLOT = (
    "{"
    '"Id": "NIC.Slot.1-1-1",'
    '"MACAddress": "F8:BC:12:22:89:E1",'
    '"Name": "System Ethernet Interface",'
    '"SpeedMbps": 10240,'
    '"Status": {"Health": "OK", "State": "Enabled"}'
    "}"
)
ETHERNET_INTERFACES_RESP_NIC_INT = (
    "{"
    '"Id": "NIC.Integrated.1-1-1",'
    '"MACAddress": "F8:BC:12:22:89:E0",'
    '"Name": "System Ethernet Interface",'
    '"SpeedMbps": 10240,'
    '"Status": {"Health": "OK", "State": "Enabled"}'
    "}"
)
NETWORK_ADAPTERS_RESP = (
    '{"Members": ['
    f'{{"@odata.id": "/redfish/v1/Chassis/System.Embedded.1/NetworkAdapters/{DEVICE_NIC_I}"}},'
    f'{{"@odata.id": "/redfish/v1/Chassis/System.Embedded.1/NetworkAdapters/{DEVICE_NIC_S}"}}'
    "]}"
)
NETWORK_PORTS_ROOT_RESP = (
    '{"Members": ['
    '{"@odata.id": "/redfish/v1/Chassis/System.Embedded.1/NetworkAdapters/%s/NetworkPorts/%s-1"} '
    "]}"
)
NETWORK_DEV_FUNC_RESP = (
    '{"Members": ['
    '{"@odata.id": "/redfish/v1/Chassis/System.Embedded.1/NetworkAdapters/%s/NetworkDeviceFunctions/%s-1"}'
    "]}"
)
NETWORK_DEV_FUNC_DET_RESP = (
    '{"Ethernet": {"MACAddress": "B0:26:28:D8:68:C0"},'
    '"Oem": {"Dell": {"DellNIC": {"VendorName": "Intel"}}}}'
)
NETWORK_PORTS_RESP = '{"Id": "%s-1", "LinkStatus": "Down", "SupportedLinkCapabilities": [{"LinkSpeedMbps": 1000}]}'
RESPONSE_LS_INTERFACES = (
    "- INFO     - NIC.Integrated.1-1:\n"
    "- INFO     -     Id: NIC.Integrated.1-1\n"
    "- INFO     -     LinkStatus: Down\n"
    "- INFO     -     LinkSpeedMbps: 1000\n"
    "- INFO     -     MACAddress: B0:26:28:D8:68:C0\n"
    "- INFO     -     Vendor: Intel\n"
    "- INFO     - NIC.Slot.1-1:\n"
    "- INFO     -     Id: NIC.Slot.1-1\n"
    "- INFO     -     LinkStatus: Down\n"
    "- INFO     -     LinkSpeedMbps: 1000\n"
    "- INFO     -     MACAddress: B0:26:28:D8:68:C0\n"
    "- INFO     -     Vendor: Intel\n"
)
RESPONSE_LS_ETHERNET = (
    "- INFO     - NIC.Slot.1-1-1:\n"
    "- INFO     -     Name: System Ethernet Interface\n"
    "- INFO     -     MACAddress: F8:BC:12:22:89:E1\n"
    "- INFO     -     Health: OK\n"
    "- INFO     -     SpeedMbps: 10240\n"
    "- INFO     - NIC.Integrated.1-1-1:\n"
    "- INFO     -     Name: System Ethernet Interface\n"
    "- INFO     -     MACAddress: F8:BC:12:22:89:E0\n"
    "- INFO     -     Health: OK\n"
    "- INFO     -     SpeedMbps: 10240\n"
)
RESPONSE_LS_INTERFACES_NOT_SUPPORTED = (
    "- ERROR    - Server does not support this functionality\n"
)
RESPONSE_LS_INTERFACES_VALUE_ERROR = (
    "- ERROR    - There was something wrong getting network interfaces\n"
)

INTERFACES_RESP = f'{{"Id":"NIC.Integrated.1-2-1","MACAddress":"{MAC_ADDRESS}"}}'

RESPONSE_LS_JOBS = (
    f"- INFO     - Found active jobs:\n" f"- INFO     -     JobID: {JOB_ID}\n"
)
RESPONSE_LS_JOBS_EMPTY = "- INFO     - Found active jobs: None\n"
RESPONSE_CLEAR_JOBS = (
    f"- INFO     - Job queue for iDRAC {MOCK_HOST} successfully cleared.\n"
)
RESPONSE_CHECK_JOB = (
    f"- INFO     - JobID: {JOB_ID}\n"
    "- INFO     - Name: Task\n"
    "- INFO     - Message: Job completed successfully.\n"
    "- INFO     - PercentComplete: 100\n"
)
RESPONSE_CHECK_JOB_BAD = (
    "- ERROR    - Command failed to check job status, return code is 404\n"
)
RESPONSE_CHECK_JOB_ERROR = "- ERROR    - Command failed to check job status\n"

DELLJOBSERVICE_UNSUPPORTED = (
    "- WARNING  - iDRAC version installed does not support DellJobService\n"
)
RESPONSE_CLEAR_JOBS_UNSUPPORTED = f"{DELLJOBSERVICE_UNSUPPORTED}{RESPONSE_CLEAR_JOBS}"
RESPONSE_CLEAR_JOBS_LIST = f"{DELLJOBSERVICE_UNSUPPORTED}- WARNING  - Clearing job queue for job IDs: ['{JOB_ID}'].\n{RESPONSE_CLEAR_JOBS}"
RESPONSE_CLEAR_JOBS_LIST_EXCEPTION = (
    "- WARNING  - iDRAC version installed does not support DellJobService\n"
    "- WARNING  - Clearing job queue for job IDs: ['JID_498218641680'].\n"
    "- INFO     - Attempting to clear job list instead.\n"
    "- WARNING  - Clearing job queue for job IDs: ['JID_498218641680'].\n"
    "- ERROR    - Job queue not cleared, there was something wrong with your request.\n"
)
RESPONSE_DELETE_JOBS_UNSUPPORTED_EXCEPTION = (
    "- WARNING  - iDRAC version installed does not support DellJobService\n"
    "- INFO     - Attempting to clear job list instead.\n"
    "- WARNING  - Clearing job queue for job IDs: ['JID_498218641680'].\n"
    "- ERROR    - Failed to communicate with server.\n"
)
RESPONSE_DELETE_JOBS_SUPPORTED_EXCEPTION = (
    "- ERROR    - Error reading response from host.\n"
)

FIRMWARE_INVENTORY_RESP = (
    '{"Members": ['
    '{"@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/Installed-0-16.25.40.62"},'
    '{"@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/Installed-0-19.5.12"}'
    "]} "
)
FIRMWARE_INVENTORY_1_RESP = (
    "{"
    '"Id": "Installed-0-16.25.40.62",'
    '"Name": "Mellanox ConnectX-5",'
    '"ReleaseDate": "00:00:00Z",'
    '"SoftwareId": "0",'
    '"Status": {"Health": "OK","State": "Enabled"},'
    '"Updateable": "True",'
    '"Version": "16.25.40.62"}'
)
FIRMWARE_INVENTORY_2_RESP = (
    "{"
    '"Id": "Installed-0-19.5.12",'
    '"Name": "Intel(R) Ethernet Network Adapter",'
    '"ReleaseDate": "00:00:00Z",'
    '"SoftwareId": "0",'
    '"Status": {"Health": "OK","State": "Enabled"},'
    '"Updateable": "True",'
    '"Version": "19.5.12"}'
)
FIRMWARE_INVENTORY_RESP_CONTAINING_ERROR = (
    '{"error": "Something went wrong when getting firmware inventory"}'
)
RESPONSE_FIRMWARE_INVENTORY = (
    "- INFO     - Installed-0-16.25.40.62:\n"
    "- INFO     -     Id: Installed-0-16.25.40.62\n"
    "- INFO     -     Name: Mellanox ConnectX-5\n"
    "- INFO     -     ReleaseDate: 00:00:00Z\n"
    "- INFO     -     SoftwareId: 0\n"
    "- INFO     -     Status: {'Health': 'OK', 'State': 'Enabled'}\n"
    "- INFO     -     Updateable: True\n"
    "- INFO     -     Version: 16.25.40.62\n"
    "- INFO     - Installed-0-19.5.12:\n"
    "- INFO     -     Id: Installed-0-19.5.12\n"
    "- INFO     -     Name: Intel(R) Ethernet Network Adapter\n"
    "- INFO     -     ReleaseDate: 00:00:00Z\n"
    "- INFO     -     SoftwareId: 0\n"
    "- INFO     -     Status: {'Health': 'OK', 'State': 'Enabled'}\n"
    "- INFO     -     Updateable: True\n"
    "- INFO     -     Version: 19.5.12\n"
)
RESPONSE_FIRMWARE_INVENTORY_NOT_ABLE_TO_ACCESS = (
    "- ERROR    - Not able to access Firmware inventory.\n"
)
RESPONSE_FIRMWARE_INVENTORY_NONE_RESPONSE = (
    "- INFO     - Installed-0-16.25.40.62:\n"
    "- INFO     -     Id: Installed-0-16.25.40.62\n"
    "- INFO     -     Name: Mellanox ConnectX-5\n"
    "- INFO     -     ReleaseDate: 00:00:00Z\n"
    "- INFO     -     SoftwareId: 0\n"
    "- INFO     -     Status: {'Health': 'OK', 'State': 'Enabled'}\n"
    "- INFO     -     Updateable: True\n"
    "- INFO     -     Version: 16.25.40.62\n"
)

MEMORY_MEMBERS_RESP = (
    '{"Members": ['
    '{"@odata.id": "/redfish/v1/Systems/System.Embedded.1/Memory/DIMM.Socket.A5"},'
    '{"@odata.id": "/redfish/v1/Systems/System.Embedded.1/Memory/DIMM.Socket.B2"}]}'
)
MEMORY_SUMMARY_RESP = (
    '{"MemorySummary": {'
    '"MemoryMirroring": "System",'
    '"Status": {"Health": "Unknown","HealthRollup": "Unknown","State": "Enabled"},'
    '"TotalSystemMemoryGiB": 384}}'
)
MEMORY_A5_RESP = (
    '{"CapacityMiB": 32768,'
    '"Description": "DIMM A5",'
    '"Manufacturer": "Hynix Semiconductor",'
    '"MemoryDeviceType": "DDR4",'
    '"Name": "DIMM A5",'
    '"OperatingSpeedMhz": 2933}'
)
MEMORY_B2_RESP = (
    '{"CapacityMiB": 32768,'
    '"Description": "DIMM B2",'
    '"Manufacturer": "Hynix Semiconductor",'
    '"MemoryDeviceType": "DDR4",'
    '"Name": "DIMM B2",'
    '"OperatingSpeedMhz": 2933}'
)
RESPONSE_LS_MEMORY = (
    "- INFO     - Memory Summary:\n"
    "- INFO     -     MemoryMirroring: System\n"
    "- INFO     -     TotalSystemMemoryGiB: 384\n"
    "- INFO     - DIMM A5:\n"
    "- INFO     -     CapacityMiB: 32768\n"
    "- INFO     -     Description: DIMM A5\n"
    "- INFO     -     Manufacturer: Hynix Semiconductor\n"
    "- INFO     -     MemoryDeviceType: DDR4\n"
    "- INFO     -     OperatingSpeedMhz: 2933\n"
    "- INFO     - DIMM B2:\n"
    "- INFO     -     CapacityMiB: 32768\n"
    "- INFO     -     Description: DIMM B2\n"
    "- INFO     -     Manufacturer: Hynix Semiconductor\n"
    "- INFO     -     MemoryDeviceType: DDR4\n"
    "- INFO     -     OperatingSpeedMhz: 2933\n"
)
RESPONSE_LS_MEMORY_SUMMARY_VALUE_ERROR = (
    "- ERROR    - There was something wrong getting memory summary\n"
)
MEMORY_SUMMARY_RESP_FAULTY = (
    '{"MemorySum": {'
    '"MemoryMirroring": "System",'
    '"Status": {"Health": "Unknown","HealthRollup": "Unknown","State": "Enabled"},'
    '"TotalSystemMemoryGiB": 384}}'
)
RESPONSE_LS_MEMORY_SUMMARY_PROC_DATA_ERROR = (
    "- ERROR    - Server does not support this functionality\n"
)
RESPONSE_LS_MEMORY_DETAILS_NOT_FOUND = (
    "- INFO     - Memory Summary:\n"
    "- INFO     -     MemoryMirroring: System\n"
    "- INFO     -     TotalSystemMemoryGiB: 384\n"
    "- ERROR    - Server does not support this functionality\n"
)
RESPONSE_LS_MEMORY_DETAILS_VALUE_ERROR = (
    "- INFO     - Memory Summary:\n"
    "- INFO     -     MemoryMirroring: System\n"
    "- INFO     -     TotalSystemMemoryGiB: 384\n"
    "- ERROR    - There was something wrong getting memory details\n"
)

PROCESSOR_SUMMARY_RESP = (
    '{"ProcessorSummary": {'
    '"Count": 2,'
    '"LogicalProcessorCount": 80,'
    '"Model": "Intel(R) Xeon(R) Gold 6230 CPU @ 2.10GHz",'
    '"Status": {"Health": "Unknown","HealthRollup": "Unknown","State": "Enabled"}}}'
)
PROCESSOR_MEMBERS_RESP = (
    '{"Members": ['
    '{"@odata.id": "/redfish/v1/Systems/System.Embedded.1/Processors/CPU.Socket.1"},'
    '{"@odata.id": "/redfish/v1/Systems/System.Embedded.1/Processors/CPU.Socket.2"}]}'
)
PROCESSOR_CPU_RESP = (
    '{"InstructionSet": "x86-64",'
    '"Id": "CPU.Socket.%s",'
    '"Manufacturer": "Intel",'
    '"MaxSpeedMHz": 4000,'
    '"Model": "Intel(R) Xeon(R) Gold 6230 CPU @ 2.10GHz",'
    '"Name": "CPU %s",'
    '"TotalCores": 20,'
    '"TotalThreads": 40}'
)
RESPONSE_LS_PROCESSORS = (
    "- INFO     - Processor Summary:\n"
    "- INFO     -     Count: 2\n"
    "- INFO     -     LogicalProcessorCount: 80\n"
    "- INFO     -     Model: Intel(R) Xeon(R) Gold 6230 CPU @ 2.10GHz\n"
    "- INFO     - CPU.Socket.1:\n"
    "- INFO     -     Name: CPU 1\n"
    "- INFO     -     InstructionSet: x86-64\n"
    "- INFO     -     Manufacturer: Intel\n"
    "- INFO     -     MaxSpeedMHz: 4000\n"
    "- INFO     -     Model: Intel(R) Xeon(R) Gold 6230 CPU @ 2.10GHz\n"
    "- INFO     -     TotalCores: 20\n"
    "- INFO     -     TotalThreads: 40\n"
    "- INFO     - CPU.Socket.2:\n"
    "- INFO     -     Name: CPU 2\n"
    "- INFO     -     InstructionSet: x86-64\n"
    "- INFO     -     Manufacturer: Intel\n"
    "- INFO     -     MaxSpeedMHz: 4000\n"
    "- INFO     -     Model: Intel(R) Xeon(R) Gold 6230 CPU @ 2.10GHz\n"
    "- INFO     -     TotalCores: 20\n"
    "- INFO     -     TotalThreads: 40\n"
)
PROCESSOR_SUMMARY_RESP_FAULTY = (
    '{"ProcessorSum": {'
    '"Count": 2,'
    '"LogicalProcessorCount": 80,'
    '"Model": "Intel(R) Xeon(R) Gold 6230 CPU @ 2.10GHz",'
    '"Status": {"Health": "Unknown","HealthRollup": "Unknown","State": "Enabled"}}}'
)
RESPONSE_LS_PROCESSORS_SUMMARY_PROC_DATA_ERROR = (
    "- ERROR    - Server does not support this functionality\n"
)
RESPONSE_LS_PROCESSORS_SUMMARY_VALUE_ERROR = (
    "- ERROR    - There was something wrong getting processor summary\n"
)
RESPONSE_LS_PROCESSORS_DETAILS_NOT_FOUND = (
    "- INFO     - Processor Summary:\n"
    "- INFO     -     Count: 2\n"
    "- INFO     -     LogicalProcessorCount: 80\n"
    "- INFO     -     Model: Intel(R) Xeon(R) Gold 6230 CPU @ 2.10GHz\n"
    "- ERROR    - Server does not support this functionality\n"
)
RESPONSE_LS_PROCESSORS_DETAILS_VALUE_ERROR = (
    "- INFO     - Processor Summary:\n"
    "- INFO     -     Count: 2\n"
    "- INFO     -     LogicalProcessorCount: 80\n"
    "- INFO     -     Model: Intel(R) Xeon(R) Gold 6230 CPU @ 2.10GHz\n"
    "- ERROR    - There was something wrong getting processor details\n"
)

DELL_REDFISH_ROOT_OEM_RESP = """
    {"Oem":
        {"Dell":
            {"@odata.context":"/redfish/v1/$metadata#DellServiceRoot.DellServiceRoot",
             "@odata.type":"#DellServiceRoot.v1_0_0.DellServiceRoot",
             "IsBranded":0,
             "ManagerMACAddress":"f4:13:37:ee:30:69",
             "ServiceTag":"HXVMC42"}
        }
    }
"""
SYSTEM_SERIAL_NUMBER_RESP = """
    {"@odata.id":"/redfish/v1/Systems/1",
    "Id":"1", "Name":"System",
    "Description":"Description of server",
    "SerialNumber":"S211337X8693420",
    "Manufacturer":"Supermicro",
    "Model":"SYS-5039MS-HUH4F" }
"""
EMPTY_OEM_RESP = '{"Oem":{}}'
RESPONSE_LS_SERIAL_SERVICE_TAG = (
    "- INFO     - ServiceTag:\n" "- INFO     -     f01-h01-000-r630.host.io: HXVMC42\n"
)
RESPONSE_LS_SERIAL_NUMBER = (
    "- INFO     - Serial Number:\n"
    "- INFO     -     f01-h01-000-r630.host.io: S211337X8693420\n"
)
RESPONSE_LS_SERIAL_UNSUPPORTED = (
    "- ERROR    - Server does not support this functionality\n"
)
RESPONSE_LS_SERIAL_SOMETHING_WRONG = (
    "- ERROR    - There was something wrong getting serial summary\n"
)

BLANK_RESP = '"OK"'
TASK_OK_RESP = (
    '{"Message": "Job completed successfully.","Id": "%s","Name": "Task","PercentComplete": "100"}'
    % JOB_ID
)
JOB_OK_RESP = '{"JobID": "%s"}' % JOB_ID
SCREENSHOT_64 = base64.b64encode(bytes("ultimate_screenshot", "utf-8"))
SCREENSHOT_RESP = '{"ServerScreenShotFile": "%s"}' % str(SCREENSHOT_64)
MOCK_HOST_SHORT_FQDN = MOCK_HOST.split(".")[0]
SCREENSHOT_NAME = f"{MOCK_HOST_SHORT_FQDN}_screenshot_now.png"
GIF_NAME = f"{MOCK_HOST_SHORT_FQDN}_screenshot_now.gif"
SCREENSHOT_NOT_SUPPORTED = "- ERROR    - The system does not support screenshots.\n"
SCREENSHOT_BAD_REQUEST = (
    "- ERROR    - POST command failed to get the server screenshot.\n"
    "- ERROR    - {'ServerScreenShotFile': \"%s\"}\n" % str(SCREENSHOT_64)
)
SCREENSHOT_FALSE_OK = "- ERROR    - Error reading response from host.\n"
SCREENSHOT_GIF_FALSE_OK = (
    "- ERROR    - POST command failed to get the server screenshot.\n"
    "- ERROR    - Error reading response from host.\n"
)

VMEDIA_CONFIG_NO_RESOURCE = "- ERROR    - Not able to access virtual media resource.\n"
VMEDIA_CONFIG_NO_CONFIG = "- ERROR    - Not able to access virtual media config.\n"
VMEDIA_GET_VM_CONFIG_RESP_DELL = """
{
    "@odata.context":"/redfish/v1/$metadata#VirtualMediaCollection.VirtualMediaCollection",
    "@odata.id":"/redfish/v1/Managers/iDRAC.Embedded.1/VirtualMedia",
    "@odata.type":"#VirtualMediaCollection.VirtualMediaCollection",
    "Description":"iDRAC Virtual Media Services Settings",
    "Members":[
        {"@odata.id":"/redfish/v1/Managers/iDRAC.Embedded.1/VirtualMedia/RemovableDisk"},
        {"@odata.id":"/redfish/v1/Managers/iDRAC.Embedded.1/VirtualMedia/CD"}
    ],
    "Members@odata.count":2,
    "Name":"Virtual Media Services"
}
"""
VMEDIA_GET_VM_CONFIG_RESP_SM = """
{
    "@odata.context":"/redfish/v1/$metadata#VirtualMediaCollection.VirtualMediaCollection",
    "@odata.type":"#VirtualMediaCollection.VirtualMediaCollection",
    "@odata.id":"/redfish/v1/Managers/1/VM1",
    "Name":"Virtual Media Collection",
    "Description":"Collection of Virtual Media for this System",
    "Members@odata.count":0,
    "Oem":{
        "Supermicro":{
            "@odata.type":"#SmcVirtualMediaExtensions.v1_0_0.VirtualMediaCollection",
            "VirtualMediaConfig":{
                "@odata.id":"/redfish/v1/Managers/1/VM1/CfgCD"
            }
        }
    }
}
"""
VMEDIA_GET_VM_CONFIG_RESP_SM_WITH_MEMBERS = """
{
    "@odata.context": "/redfish/v1/$metadata#VirtualMediaCollection.VirtualMediaCollection",
    "@odata.type": "#VirtualMediaCollection.VirtualMediaCollection",
    "@odata.id": "/redfish/v1/Managers/1/VM1",
    "Name": "Virtual Media Collection",
    "Description": "Collection of Virtual Media for this System",
    "Members": [
        {
            "@odata.id": "/redfish/v1/Managers/1/VM1/CD1"
        }
    ],
    "Members@odata.count": 1,
    "Oem": {
        "Supermicro": {
            "@odata.type": "#SmcVirtualMediaExtensions.v1_0_0.VirtualMediaCollection",
            "VirtualMediaConfig": {
                "@odata.id": "/redfish/v1/Managers/1/VM1/CfgCD"
            }
        }
    }
}
"""
VMEDIA_GET_VM_CONFIG_EMPTY_RESP_SM = "- INFO     - No virtual media mounted.\n"
VMEDIA_GET_MEMBERS_RESP_DELL = """
{"Members": [
    {"@odata.id": "/redfish/v1/Managers/iDRAC.Embedded.1/VirtualMedia/RemovableDisk"},
    {"@odata.id": "/redfish/v1/Managers/iDRAC.Embedded.1/VirtualMedia/CD"}
  ]
}
"""
VMEDIA_MEMBER_RM_DISK_RESP = """
{
  "Id":"RemovableDisk",
  "ImageName":null,
  "Inserted":false,
  "Name":"Virtual Removable Disk"
}
"""
VMEDIA_MEMBER_CD_RESP = """
{
  "Id":"CD",
  "ImageName":"TestImage",
  "Inserted":true,
  "Name":"Virtual CD"
}
"""
VMEDIA_CHECK_GOOD_DELL = """\
- INFO     - RemovableDisk:\n\
- INFO     -     Name: Virtual Removable Disk\n\
- INFO     -     ImageName: None\n\
- INFO     -     Inserted: False\n\
- INFO     - CD:\n\
- INFO     -     Name: Virtual CD\n\
- INFO     -     ImageName: TestImage\n\
- INFO     -     Inserted: True\n\
"""
VMEDIA_CHECK_GOOD_SM = """\
- INFO     - CD:\n\
- INFO     -     Name: Virtual CD\n\
- INFO     -     ImageName: TestImage\n\
- INFO     -     Inserted: True\n\
"""
VMEDIA_GET_ENDPOINT_FALSE = '{"VirtualMedia":false}'
VMEDIA_GET_ENDPOINT_EMPTY = '{"VirtualMedia": {"@odata.id":false}}'
VMEDIA_CHECK_EMPTY = """\
- WARNING  - No active VirtualMedia found\n\
"""

VMEDIA_MOUNT_SUCCESS = "- INFO     - Image mounting operation was successful.\n"
VMEDIA_MOUNT_NOT_ALLOWED = (
    "- ERROR    - Virtual media mounting is not allowed on this server.\n"
)
VMEDIA_MOUNT_ALREADY_FILLED = "- ERROR    - Couldn't mount virtual media, because there is virtual media mounted already.\n"
VMEDIA_MOUNT_SOMETHING_WRONG = (
    "- ERROR    - There was something wrong trying to mount virtual media.\n"
)

VMEDIA_UNMOUNT_SUCCESS = "- INFO     - Image unmount operation was successful.\n"
VMEDIA_UNMOUNT_NOT_ALLOWED = (
    "- ERROR    - Virtual media unmounting is not allowed on this server.\n"
)
VMEDIA_UNMOUNT_EMPTY = "- ERROR    - Couldn't unmount virtual media, because there isn't any virtual media mounted.\n"
VMEDIA_UNMOUNT_SOMETHING_WRONG = (
    "- ERROR    - There was something wrong trying to unmount virtual media.\n"
)

VMEDIA_BOOT_TO_NO_MEDIA = "- ERROR    - No virtual CD is inserted.\n"
VMEDIA_BOOT_TO_MISSING = (
    "- ERROR    - Device Optical.iDRACVirtual.1-1 does not match any of the "
    f"available boot devices for host {MOCK_HOST}\n"
    "- ERROR    - Command failed to set next onetime boot to virtual media. No virtual optical media boot device.\n"
)
VMEDIA_BOOT_TO_SM_PASS = (
    "- INFO     - Command passed to set next onetime boot device to virtual media.\n"
)
VMEDIA_BOOT_TO_SM_FAIL = (
    "- ERROR    - Command failed to set next onetime boot device to virtual media.\n"
)
BOOT_SOURCE_OVERRIDE_TARGET_USBCD = """
{
    "Boot": {
        "BootSourceOverrideTarget@Redfish.AllowableValues": [
            "None", "Pxe", "Hdd", "Diags", "CD/DVD",
            "BiosSetup", "FloppyRemovableMedia",
            "UsbKey", "UsbHdd", "UsbFloppy", "UsbCd",
            "UefiUsbKey", "UefiCd", "UefiHdd",
            "UefiUsbHdd", "UefiUsbCd"
        ]
    }
}
"""
BOOT_SOURCE_OVERRIDE_TARGET_CD = """
{
    "Boot": {
        "BootSourceOverrideTarget@Redfish.AllowableValues": [
            "None", "Pxe", "Floppy", "Cd",
            "Usb", "Hdd", "BiosSetup"
        ]
    }
}
"""
VMEDIA_CHECK_DISC_VALUE_ERROR = (
    "- ERROR    - There was something wrong getting values for VirtualMedia\n"
)
VMEDIA_NO_ENDPOINT_ERROR = "- ERROR    - No VirtualMedia endpoint found\n"

VMEDIA_OS_DEPLOYMENT_NOT_SUPPORTED = (
    "- ERROR    - iDRAC version installed doesn't support DellOSDeploymentService needed for this feature.\n"
)
VMEDIA_REMOTE_CHECK_RESP = """
{
    "@Message.ExtendedInfo": [{
        "Message":"Successfully Completed Request",
        "MessageArgs":[],
        "MessageArgs@odata.count":0,
        "MessageId":"Base.1.5.Success",
        "RelatedProperties":[],
        "RelatedProperties@odata.count":0,
        "Resolution":"None"
        ,"Severity":"OK"
    }],
    "DriversAttachStatus":"NotAttached",
    "ISOAttachStatus":"Attached"
}
"""
VMEDIA_REMOTE_CHECK_GOOD = "- INFO     - Current ISO attach status: Attached\n"
VMEDIA_REMOTE_CHECK_FAIL = "- ERROR    - Command failed to get attach status of the remote mounted ISO.\n"
VMEDIA_REMOTE_CHECK_ERROR = "- ERROR    - There was something wrong trying to check remote image attach status.\n"
VMEDIA_REMOTE_BOOT_TASK_RESP = """
{
    "@odata.context":"/redfish/v1/$metadata#Task.Task",
    "@odata.id":"/redfish/v1/TaskService/Tasks/OSDeployment",
    "@odata.type":"#Task.v1_4_2.Task",
    "Description":"Server Configuration and other Tasks running on iDRAC are listed here",
    "EndTime":"",
    "Id":"OSDeployment",
    "Messages":[{
        "Message":"",
        "MessageArgs":[],
        "MessageArgs@odata.count":0,
        "MessageId":""
    }],
    "Messages@odata.count":1,
    "Name":"BootToNetworkISO",
    "PercentComplete":null,
    "TaskState":"Running",
    "TaskStatus":"OK"
}
"""
VMEDIA_REMOTE_BOOT_TASK_FAILED_RESP = """
{
    "@odata.context":"/redfish/v1/$metadata#Task.Task",
    "@odata.id":"/redfish/v1/TaskService/Tasks/OSDeployment",
    "@odata.type":"#Task.v1_4_2.Task",
    "Description":"Server Configuration and other Tasks running on iDRAC are listed here",
    "EndTime":"",
    "Id":"OSDeployment",
    "Messages":[{
        "Message":"",
        "MessageArgs":[],
        "MessageArgs@odata.count":0,
        "MessageId":""
    }],
    "Messages@odata.count":1,
    "Name":"BootToNetworkISO",
    "PercentComplete":null,
    "TaskState":"Failed",
    "TaskStatus":"Error"
}
"""
VMEDIA_REMOTE_BOOT_GOOD = (
    "- INFO     - Command for booting to remote ISO was successful, job was created.\n"
    "- INFO     - OSDeployment task status is OK.\n"
)
VMEDIA_REMOTE_BOOT_WRONG_PATH = "- ERROR    - Wrong NFS path format.\n"
VMEDIA_REMOTE_BOOT_COMMAND_FAIL = "- ERROR    - Command failed to boot to remote ISO. No job was created.\n"
VMEDIA_REMOTE_BOOT_TASK_FAIL = (
    "- INFO     - Command for booting to remote ISO was successful, job was created.\n"
    "- ERROR    - OSDeployment task failed and couldn't be completed.\n"
)
VMEDIA_REMOTE_BOOT_SOMETHING_WRONG = (
    "- INFO     - Command for booting to remote ISO was successful, job was created.\n"
    "- ERROR    - There was something wrong trying to check remote image attach status.\n"
)
VMEDIA_REMOTE_DETACH_GOOD = "- INFO     - Command to detach remote ISO was successful.\n"
VMEDIA_REMOTE_DETACH_FAIL = "- ERROR    - Command failed to detach remote mounted ISO.\n"

BIOS_PASS_SET_GOOD = f"""\
- INFO     - Command passed to set BIOS password.
- WARNING  - Host will now be rebooted for changes to take place.
- INFO     - Command passed to On server, code return is 200.
- INFO     - JobID: {JOB_ID}
- INFO     - Name: Task
- INFO     - Message: Job completed successfully.
- INFO     - PercentComplete: 100
"""
BIOS_PASS_SET_MISS_ARG = """\
- ERROR    - Missing argument: `--new-password`
"""
BIOS_PASS_RM_GOOD = (
    """\
- INFO     - Command passed to set BIOS password.
- WARNING  - Host will now be rebooted for changes to take place.
- INFO     - Command passed to On server, code return is 200.
- INFO     - JobID: %s
- INFO     - Name: Task
- INFO     - Message: Job completed successfully.
- INFO     - PercentComplete: 100
"""
    % JOB_ID
)
BIOS_PASS_RM_MISS_ARG = """\
- ERROR    - Missing argument: `--old-password`
"""
BIOS_PASS_CHANGE_NOT_SUPPORTED = (
    "- ERROR    - BIOS password change not supported on this system.\n"
)
BIOS_PASS_CHANGE_CMD_FAILED = (
    "- WARNING  - Command failed to set BIOS password\n"
    "- ERROR    - Error reading response from host.\n"
)
BIOS_PASS_SET_CHECK_JOB_STATUS_BAD_CODE = (
    "- INFO     - Command passed to set BIOS password.\n"
    "- WARNING  - Host will now be rebooted for changes to take place.\n"
    "- INFO     - Command passed to On server, code return is 200.\n"
    "- ERROR    - Command failed to check job status, return code is 400\n"
)
BIOS_PASS_SET_CHECK_JOB_STATUS_FAIL_MSG = (
    "- INFO     - Command passed to set BIOS password.\n"
    "- WARNING  - Host will now be rebooted for changes to take place.\n"
    "- INFO     - Command passed to On server, code return is 200.\n"
)
CHECK_JOB_STATUS_FAIL_MSG = '{"Message": "Fail"}'
CHECK_JOB_STATUS_UNEXPECTED_MSG_CONTENT = '{"Message": "Unexpected content"}'

ATTRIBUTE_OK = "ProcC1E"
ATTRIBUTE_BAD = "NotThere"
ATTR_VALUE_OK = "Enabled"
ATTR_VALUE_BAD = "NotAllowed"
ATTR_VALUE_DIS = "Disabled"

BIOS_RESPONSE_OK = '{"Attributes":{"%s": "%s"}}' % (ATTRIBUTE_OK, ATTR_VALUE_OK)
BIOS_RESPONSE_DIS = '{"Attributes":{"%s": "%s"}}' % (ATTRIBUTE_OK, ATTR_VALUE_DIS)
BIOS_REGISTRY_BASE = '{"RegistryEntries": {"Attributes": %s}}'
BIOS_RESPONSE_SRIOV = '{"Attributes":{"SriovGlobalEnable": "%s"}}'
BIOS_REGISTRY_1 = {
    "AttributeName": "SystemModelName",
    "CurrentValue": "None",
    "DisplayName": "System Model Name",
    "DisplayOrder": 200,
    "HelpText": "Indicates the product name of the system.",
    "Hidden": "False",
    "Immutable": "True",
    "MaxLength": 40,
    "MenuPath": "./SysInformationRef",
    "MinLength": 0,
    "ReadOnly": "True",
    "ResetRequired": "True",
    "Type": "String",
    "ValueExpression": "None",
    "WriteOnly": "False",
}
BIOS_REGISTRY_2 = {
    "AttributeName": "ProcC1E",
    "CurrentValue": "None",
    "DisplayName": "C1E",
    "DisplayOrder": 9604,
    "HelpText": "When set to Enabled, the processor is allowed to switch to minimum performance state when idle.",
    "Hidden": "False",
    "Immutable": "False",
    "MenuPath": "./SysProfileSettingsRef",
    "ReadOnly": "False",
    "ResetRequired": "True",
    "Type": "Enumeration",
    "Value": [
        {"ValueDisplayName": "Enabled", "ValueName": "Enabled"},
        {"ValueDisplayName": "Disabled", "ValueName": "Disabled"},
    ],
    "WarningText": "None",
    "WriteOnly": "False",
}
BIOS_REGISTRY_OK = BIOS_REGISTRY_BASE % str([BIOS_REGISTRY_1, BIOS_REGISTRY_2])
BIOS_SET_OK = """\
- INFO     - Command passed to set BIOS attribute pending values.
- INFO     - Command passed to GracefulRestart server, code return is 200.
- INFO     - Polling for host state: Not Down
- INFO     - Command passed to On server, code return is 200.
"""
BIOS_SET_BAD_VALUE = (
    """\
- WARNING  - List of accepted values for '%s': ['Enabled', 'Disabled']
- ERROR    - Value not accepted
"""
    % ATTRIBUTE_OK
)
BIOS_SET_BAD_ATTR = """\
- WARNING  - Could not retrieve Bios Attributes.
- ERROR    - NotThere not found. Please check attribute name.
- ERROR    - Attribute not found
"""
BIOS_GET_ALL_OK = f"""- INFO     - {ATTRIBUTE_OK}: {ATTR_VALUE_OK}\n"""
BIOS_GET_ONE_OK = """\
- INFO     - AttributeName: ProcC1E
- INFO     - CurrentValue: Enabled
- INFO     - DisplayName: C1E
- INFO     - DisplayOrder: 9604
- INFO     - HelpText: When set to Enabled, the processor is allowed to switch to minimum performance state when idle.
- INFO     - Hidden: False
- INFO     - Immutable: False
- INFO     - MenuPath: ./SysProfileSettingsRef
- INFO     - ReadOnly: False
- INFO     - ResetRequired: True
- INFO     - Type: Enumeration
- INFO     - Value: [{'ValueDisplayName': 'Enabled', 'ValueName': 'Enabled'}, {'ValueDisplayName': 'Disabled', 'ValueName': 'Disabled'}]
- INFO     - WarningText: None
- INFO     - WriteOnly: False
"""
BIOS_GET_ONE_BAD = (
    """\
- WARNING  - Could not retrieve Bios Attributes.
- ERROR    - Unable to locate the Bios attribute: %s
"""
    % ATTRIBUTE_BAD
)
NEXT_BOOT_PXE_OK = '- INFO     - PATCH command passed to set next boot onetime boot device to: "Pxe".\n'
NEXT_BOOT_PXE_BAD = (
    "- ERROR    - Command failed, error code is 400.\n"
    "- ERROR    - Error reading response from host.\n"
)

SRIOV_ALREADY = "- WARNING  - SRIOV mode is already in that state. IGNORING.\n"
SRIOV_STATE = "- INFO     - Enabled\n"

IMAGE_SAVED = """- INFO     - Image saved: %s\n"""

KEYBOARD_INTERRUPT = "- WARNING  - Badfish terminated\n"
WRONG_BADFISH_EXECUTION = "- WARNING  - There was something wrong executing Badfish\n"
KEYBOARD_INTERRUPT_HOST_LIST = (
    "[badfish.helpers.logger] - WARNING  - Badfish terminated\n"
)
WRONG_BADFISH_EXECUTION_HOST_LIST = "[badfish.helpers.logger] - WARNING  - There was something wrong executing Badfish\n"
SUCCESSFUL_HOST_LIST = (
    "[badfish.helpers.logger] - INFO     - RESULTS:\n"
    "[badfish.helpers.logger] - INFO     - S: SUCCESSFUL\n"
    "[badfish.helpers.logger] - INFO     - S: SUCCESSFUL\n"
    "[badfish.helpers.logger] - INFO     - S: SUCCESSFUL\n"
)
NO_HOST_ERROR = "- ERROR    - You must specify at least either a host (-H) or a host list (--host-list).\n"
HOST_LIST_EXTRAS = (
    "[f01-h01-000-r630] - ERROR    - ComputerSystem's Members array is either empty or missing\n"
    "[f01-h01-000-r630] - INFO     - ************************************************\n"
    "[f01-h01-000-r630] - ERROR    - ComputerSystem's Members array is either empty or missing\n"
    "[f01-h01-000-r630] - INFO     - ************************************************\n"
    "[f01-h01-000-r630] - ERROR    - ComputerSystem's Members array is either empty or missing\n"
    "[f01-h01-000-r630] - INFO     - ************************************************\n"
    "[badfish.helpers.logger] - INFO     - RESULTS:\n"
    "[badfish.helpers.logger] - INFO     - f01-h01-000-r630.host.io: FAILED\n"
    "[badfish.helpers.logger] - INFO     - f01-h01-000-r630.host.io: FAILED\n"
    "[badfish.helpers.logger] - INFO     - f01-h01-000-r630.host.io: FAILED\n"
)
HOST_FILE_ERROR = "[badfish.helpers.logger] - ERROR    - There was something wrong reading from non/existent/file\n"

# TEST SCP REQUESTS
SCP_GET_TARGETS_ACTIONS_OEM_WITH_ALLOWABLES = """
{
  "Actions": {
    "Oem": {
      "OemManager.v1_0_0#OemManager.ExportSystemConfiguration": {
        "ShareParameters": {
          "Target@Redfish.AllowableValues": [
            "ALL",
            "IDRAC",
            "BIOS",
            "NIC",
            "RAID"
          ]
        },
        "target": "/redfish/v1/Managers/iDRAC.Embedded.1/Actions/Oem/EID_674_Manager.ExportSystemConfiguration"
      }
    }
  }
}
"""
SCP_GET_TARGETS_ACTIONS_OEM_WITHOUT_ALLOWABLES = """
{
  "Actions": {
    "Oem": {
      "OemManager.v1_0_0#OemManager.ExportSystemConfiguration": {
        "ShareParameters": {
        },
        "target": "/redfish/v1/Managers/iDRAC.Embedded.1/Actions/Oem/EID_674_Manager.ExportSystemConfiguration"
      }
    }
  }
}
"""
SCP_GET_TARGETS_ACTIONS_OEM_UNSUPPORTED = """
{
  "Actions": {
    "Oem": {}
  }
}
"""
SCP_MESSAGE_PERCENTAGE = """\
{
    "Oem": {
        "Dell": {
            "Message": "%sporting Server Configuration Profile.",
            "PercentComplete": %d
        }
    }
}
"""
SCP_MESSAGE_PERCENTAGE_STATE = """\
{
    "Oem": {
        "Dell": {
            "Message": "%s",
            "PercentComplete": %d,
            "JobState": "%s"
        }
    }
}
"""

# TEST SCP RESPONSES
RESPONSE_GET_SCP_TARGETS_WITH_ALLOWABLES_PASS = """\
- INFO     - The allowable SCP Export targets are:
- INFO     - ALL
- INFO     - IDRAC
- INFO     - BIOS
- INFO     - NIC
- INFO     - RAID
"""
RESPONSE_GET_SCP_TARGETS_WITHOUT_ALLOWABLES_ERR = (
    "- ERROR    - Couldn't find a list of possible targets, but Export with SCP should be allowed.\n"
)
RESPONSE_GET_SCP_TARGETS_UNSUPPORTED_ERR = "- ERROR    - iDRAC on this system doesn't seem to support SCP Export.\n"
RESPONSE_GET_SCP_TARGETS_WRONG = "- ERROR    - There was something wrong trying to get targets for SCP Export.\n"

RESPONSE_EXPORT_SCP_PASS = f"""\
- INFO     - Job for exporting server configuration, successfully created. Job ID: {JOB_ID}
- INFO     - Exporting Server Configuration Profile., percent complete: 15
- INFO     - Exporting Server Configuration Profile., percent complete: 30
- INFO     - Exporting Server Configuration Profile., percent complete: 45
- INFO     - Exporting Server Configuration Profile., percent complete: 60
- INFO     - Exporting Server Configuration Profile., percent complete: 75
- INFO     - Exporting Server Configuration Profile., percent complete: 90
- INFO     - Exporting Server Configuration Profile., percent complete: 99
- INFO     - SCP export went through successfully.
- INFO     - Exported system configuration to file: ./exports/%s_targets_ALL_export.json
"""
RESPONSE_EXPORT_SCP_STATUS_FAIL = "- ERROR    - Command failed to export system configuration.\n"
RESPONSE_EXPORT_SCP_NO_LOCATION = "- ERROR    - Failed to find a job ID in headers of the response.\n"
RESPONSE_EXPORT_SCP_TIME_OUT = f"""\
- INFO     - Job for exporting server configuration, successfully created. Job ID: {JOB_ID}
- INFO     - Unable to get job status message, trying again.
- INFO     - Exporting Server Configuration Profile., percent complete: 1
- ERROR    - Job has been timed out, took longer than 5 minutes, command failed.
"""
RESPONSE_IMPORT_SCP_INVALID_FILEPATH = "- ERROR    - File doesn't exist or couldn't be opened.\n"
RESPONSE_IMPORT_SCP_STATUS_FAIL = "- ERROR    - Command failed to import system configuration.\n"
RESPONSE_IMPORT_SCP_TIME_OUT = f"""\
- INFO     - Job for importing server configuration, successfully created. Job ID: {JOB_ID}
- INFO     - Unable to locate OEM data in JSON response, trying again.
- INFO     - Unable to get job status message, trying again.
- INFO     - Importing Server Configuration Profile., percent complete: 1
- ERROR    - Job has been timed out, took longer than 5 minutes, command failed.
"""
RESPONSE_IMPORT_SCP_FAIL_STATE = f"""\
- INFO     - Job for importing server configuration, successfully created. Job ID: {JOB_ID}
- INFO     - Importing Server Configuration Profile., percent complete: 20
- INFO     - Importing Server Configuration Profile., percent complete: 40
- INFO     - Importing Server Configuration Profile., percent complete: 60
- INFO     - Unable to complete the Import operation., percent complete: 100
- ERROR    - Command failed, job status = Failed
"""

RESPONSE_IMPORT_SCP_PASS = f"""\
- INFO     - Job for importing server configuration, successfully created. Job ID: {JOB_ID}
- INFO     - Importing Server Configuration Profile., percent complete: 15
- INFO     - Importing Server Configuration Profile., percent complete: 30
- INFO     - Importing Server Configuration Profile., percent complete: 45
- INFO     - Importing Server Configuration Profile., percent complete: 60
- INFO     - Importing Server Configuration Profile., percent complete: 75
- INFO     - Importing Server Configuration Profile., percent complete: 90
- INFO     - Importing Server Configuration Profile., percent complete: 99
- INFO     - Successfully imported and applied Server Configuration Profile., percent complete: 100
- INFO     - Command passed, job successfully marked as completed. Going to reboot.
"""
