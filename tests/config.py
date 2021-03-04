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


DEVICE_HDD_1 = {
    "name": "HardDisk.List.1-1",
    "hash": "c9203080df84781e2ca3d512883dee6f"
}
DEVICE_NIC_1 = {
    "name": "NIC.Integrated.1-2-1",
    "hash": "bfa8fe2210d216298c7c53aedfc7e21b",
}
DEVICE_NIC_2 = {
    "name": "NIC.Slot.2-1-1",
    "hash": "135ac45c488549c04a21f1c199c2044a"
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
        "- ERROR    - There was something wrong executing Badfish\n"
        % (BAD_DEVICE_NAME, MOCK_HOST)
)
RESPONSE_BOOT_TO = (
    f"- WARNING  - Job queue already cleared for iDRAC {MOCK_HOST}, DELETE command will not execute.\n"
    "- INFO     - Command passed to set BIOS attribute pending values.\n"
    "- INFO     - POST command passed to create target config job.\n"
)
RESPONSE_BOOT_TO_BAD_TYPE = (
    "- ERROR    - Expected values for -t argument are: ['director', 'foreman']\n"
    "- ERROR    - There was something wrong executing Badfish\n"
)
RESPONSE_BOOT_TO_BAD_FILE = (
    "- ERROR    - No such file or directory: bad/bad/file.\n"
    "- ERROR    - There was something wrong executing Badfish\n"
)
RESPONSE_BOOT_TO_NO_FILE = (
    "- ERROR    - You must provide a path to the interfaces yaml via `-i` optional argument.\n"
    "- ERROR    - There was something wrong executing Badfish\n"
)
RESPONSE_BOOT_TO_BAD_MAC = (
    "- ERROR    - MAC Address does not match any of the existing\n"
    "- ERROR    - There was something wrong executing Badfish\n"
)

# test_reboot_only
RESPONSE_REBOOT_ONLY_SUCCESS = (
    "- INFO     - Command passed to GracefulRestart server, code return is 204.\n"
    "- INFO     - Polling for host state: Off\n"
    "- INFO     - Polling for host state: Not Down\n"
    "- INFO     - Command passed to On server, code return is 204.\n"
)

# test_reset_%s
RESPONSE_RESET = (
    "- INFO     - Status code 204 returned for POST command to reset %s.\n"
    "- INFO     - %s will now reset and be back online within a few minutes.\n"
)

# test_change_boot
RESPONSE_CHANGE_BOOT = (
    f"- WARNING  - Job queue already cleared for iDRAC {MOCK_HOST}, DELETE command will not "
    "execute.\n"
    "- INFO     - PATCH command passed to update boot order.\n"
    "- INFO     - POST command passed to create target config job.\n"
    "- INFO     - Command passed to ForceOff server, code return is 200.\n"
    "- INFO     - Polling for host state: Not Down\n"
    "- INFO     - Command passed to On server, code return is 200.\n"
)
RESPONSE_CHANGE_BAD_TYPE = (
    "- ERROR    - Expected values for -t argument are: ['director', 'foreman']\n"
    "- ERROR    - There was something wrong executing Badfish\n"
)
RESPONSE_CHANGE_TO_SAME = "- WARNING  - No changes were made since the boot order already matches the requested.\n"
RESPONSE_CHANGE_NO_INT = (
    "- ERROR    - You must provide a path to the interfaces yaml via `-i` optional argument.\n"
    "- ERROR    - There was something wrong executing Badfish\n"
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

ETHERNET_INTERFACES_RESP = (
    '{"Members":['
    '{"@odata.id":"/redfish/v1/Systems/System.Embedded.1/EthernetInterfaces/NIC.Slot.1-1-1"},'
    '{"@odata.id":"/redfish/v1/Systems/System.Embedded.1/EthernetInterfaces/NIC.Integrated.1-1-1"}'
    ']}'
)


NETWORK_ADAPTERS_RESP = (
    '{"Members": ['
    f'{{"@odata.id": "/redfish/v1/Chassis/System.Embedded.1/NetworkAdapters/{DEVICE_NIC_I}"}},'
    f'{{"@odata.id": "/redfish/v1/Chassis/System.Embedded.1/NetworkAdapters/{DEVICE_NIC_S}"}}'
    ']}'
)
NETWORK_PORTS_ROOT_RESP = (
    '{"Members": ['
    '{"@odata.id": "/redfish/v1/Chassis/System.Embedded.1/NetworkAdapters/%s/NetworkPorts/%s-1"} '
    ']}'
)
NETWORK_DEV_FUNC_RESP = (
    '{"Members": ['
    '{"@odata.id": "/redfish/v1/Chassis/System.Embedded.1/NetworkAdapters/%s/NetworkDeviceFunctions/%s-1"}'
    ']}'
)
NETWORK_DEV_FUNC_DET_RESP = (
    '{"Ethernet": {"MACAddress": "B0:26:28:D8:68:C0"},'
    '"Oem": {"Dell": {"DellNIC": {"VendorName": "Intel"}}}}'
)
NETWORK_PORTS_RESP = (
    '{"Id": "%s-1", "LinkStatus": "Down", "SupportedLinkCapabilities": [{"LinkSpeedMbps": 1000}]}'
)
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

INTERFACES_RESP = (
    f'{{"Id":"NIC.Integrated.1-2-1","MACAddress":"{MAC_ADDRESS}"}}'
)

RESPONSE_LS_JOBS = (
    "- INFO     - Found active jobs:\n"
    f"- INFO     - {JOB_ID}\n"
)
RESPONSE_CLEAR_JOBS = (
    f"- INFO     - Job queue for iDRAC {MOCK_HOST} successfully cleared.\n"
)

FIRMWARE_INVENTORY_RESP = (
    '{"Members": ['
    '{"@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/Installed-0-16.25.40.62"},'
    '{"@odata.id": "/redfish/v1/UpdateService/FirmwareInventory/Installed-0-19.5.12"}'
    ']} '
)
FIRMWARE_INVENTORY_1_RESP = (
    '{'
    '"Id": "Installed-0-16.25.40.62",'
    '"Name": "Mellanox ConnectX-5",'
    '"ReleaseDate": "00:00:00Z",'
    '"SoftwareId": "0",'
    '"Status": {"Health": "OK","State": "Enabled"},'
    '"Updateable": "True",'
    '"Version": "16.25.40.62"}'
)
FIRMWARE_INVENTORY_2_RESP = (
    '{'
    '"Id": "Installed-0-19.5.12",'
    '"Name": "Intel(R) Ethernet Network Adapter",'
    '"ReleaseDate": "00:00:00Z",'
    '"SoftwareId": "0",'
    '"Status": {"Health": "OK","State": "Enabled"},'
    '"Updateable": "True",'
    '"Version": "19.5.12"}'
)
RESPONSE_FIRMWARE_INVENTORY = (
    "- INFO     - Id: Installed-0-16.25.40.62\n"
    "- INFO     - Name: Mellanox ConnectX-5\n"
    "- INFO     - ReleaseDate: 00:00:00Z\n"
    "- INFO     - SoftwareId: 0\n"
    "- INFO     - Status: {'Health': 'OK', 'State': 'Enabled'}\n"
    "- INFO     - Updateable: True\n"
    "- INFO     - Version: 16.25.40.62\n"
    "- INFO     - ************************************************\n"
    "- INFO     - Id: Installed-0-19.5.12\n"
    "- INFO     - Name: Intel(R) Ethernet Network Adapter\n"
    "- INFO     - ReleaseDate: 00:00:00Z\n"
    "- INFO     - SoftwareId: 0\n"
    "- INFO     - Status: {'Health': 'OK', 'State': 'Enabled'}\n"
    "- INFO     - Updateable: True\n"
    "- INFO     - Version: 19.5.12\n"
    "- INFO     - ************************************************\n"
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


BLANK_RESP = '"OK"'
TASK_OK_RESP = '{"Message": "Task successfully scheduled."}'
JOB_OK_RESP = '{"JobID": "%s"}' % JOB_ID

VMEDIA_GET_VM_RESP = '{"VirtualMedia": {"@odata.id": "/redfish/v1/Managers/1/VM1"}}'
VMEDIA_GET_MEMBERS_RESP = """
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
VMEDIA_CHECK_GOOD = """\
- INFO     - ID: RemovableDisk - Name: Virtual Removable Disk - ImageName: None - Inserted: False
- INFO     - ID: CD - Name: Virtual CD - ImageName: TestImage - Inserted: True\n\
"""
VMEDIA_CHECK_EMPTY = """\
- WARNING  - No active VirtualMedia found\n\
"""
VMEDIA_GET_CONF_RESP = """
{"Oem":{
    "Supermicro":{
      "@odata.type": "#SmcVirtualMediaExtensions.v1_0_0.VirtualMediaCollection",
      "VirtualMediaConfig": {"@odata.id": "/redfish/v1/Managers/1/VM1/CfgCD"}
    }
  }
}
"""
VMEDIA_UNMOUNT_OK = "- INFO     - Successfully unmounted all VirtualMedia\n"
VMEDIA_UNMOUNT_UNSUPPORTED = "- WARNING  - OOB management does not support Virtual Media unmount\n"
